"""Host controller"""

from dataclasses import dataclass

from app.daas.adapter.adapter_ssh import SshAdapter, SshAdapterConfig
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class NodeControllerConfig:
    """Config for node requests"""

    prefixmac: str
    prefixip: str
    dnsmasqhosts: str


class NodeController(Loggable):
    """Api to control a particular node"""

    def __init__(self, cfg_net: NodeControllerConfig, cfg_ssh: SshAdapterConfig):
        Loggable.__init__(self, LogTarget.NODE)
        self.config = cfg_net
        self.config_ssh = cfg_ssh
        self.adapter = SshAdapter(cfg_ssh)
        self.connected = False

    def __str__(self):
        return "Config: " + str(self.config)

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(prefixip={self.config.prefixip},"
            f"prefixmac={self.config.prefixmac})"
        )

    def connect(self):
        """Connects the component"""
        self.connected = True
        return self.connected

    def disconnect(self) -> bool:
        """Disconnects the component"""
        self.connected = False
        return True

    def node_connection_test(self) -> int:
        """Test to check if the service is available"""
        cmd = "true"
        code, std_out, std_err = self.adapter.ssh_call(cmd)
        self._log_info(f"Connection test: {std_out}{std_err}", code)
        return code

    async def node_vmconfigure_dhcp(self, vmid: int, adr: str) -> tuple:
        """Configures dhcp for the vmid (dnsmasq)"""
        result, out, err = await self.__delete_dhcphost(vmid)
        result, out, err = await self.__add_dhcphost(vmid, adr)
        self._log_info(f"dhcp configured for {adr}")
        if result == 0:
            result, out, err = await self.__restart_dnsmasq()
        return result, out, err

    async def node_vmdelete_dhcp(self, vmid: int) -> tuple:
        """Configures dhcp for the vmid (dnsmasq)"""
        return await self.__delete_dhcphost(vmid)

    async def node_vmconfigure_iptables(self, adr: str):
        """ "Configures iptables for the vmid"""
        result, out, err = await self.__del_hostforward(adr)
        result, out, err = await self.__add_hostforward(adr)
        self._log_info(f"iptables configured for {adr}")
        return result, out, err

    async def __restart_dnsmasq(self):
        """Restarts the dnsmasq service"""
        self._log_info("Restart dnsmasq")
        cmd = "systemctl restart dnsmasq.service"
        return self.adapter.ssh_call(cmd)

    async def __del_hostforward(self, adr: str):
        """Deletes the desired host in the iptables rules"""
        # Deletes old rule
        in_rule = (
            f"iptables -D FORWARD -d {adr} "
            "-m state --state ESTABLISHED,RELATED -j ACCEPT"
        )
        out_rule = f"iptables -D FORWARD -s {adr} -j ACCEPT"
        masq_rule = f"iptables -D POSTROUTING -t nat -s {adr} -j MASQUERADE"
        in_code, in_out, in_err = self.adapter.ssh_call(in_rule)
        out_code, out_out, out_err = self.adapter.ssh_call(out_rule)
        masq_code, masq_out, masq_err = self.adapter.ssh_call(masq_rule)
        return (
            in_code + out_code + masq_code,
            f"{in_out}{out_out}{masq_out}",
            f"{in_err}{out_err}{masq_err}",
        )

    async def __add_hostforward(self, adr: str):
        """Adds the desired host in the iptables rules"""
        # Deletes old rule
        in_rule = (
            f"iptables -A FORWARD -d {adr} "
            "-m state --state ESTABLISHED,RELATED -j ACCEPT"
        )
        out_rule = f"iptables -A FORWARD -s {adr} -j ACCEPT"
        masq_rule = f"iptables -A POSTROUTING -t nat -s {adr} -j MASQUERADE"
        in_code, in_out, in_err = self.adapter.ssh_call(in_rule)
        out_code, out_out, out_err = self.adapter.ssh_call(out_rule)
        masq_code, masq_out, masq_err = self.adapter.ssh_call(masq_rule)
        return (
            in_code + out_code + masq_code,
            f"{in_out}{out_out}{masq_out}",
            f"{in_err}{out_err}{masq_err}",
        )

    async def __delete_dhcphost(self, vmid: int):
        """Deletes the desired dns host in the dnsmasq config"""
        file = f"{self.config.dnsmasqhosts}"
        sed = f"sed /{self.config.prefixmac}:{vmid:x}/d -i"
        cmd = f"[[ -f {file} ]] && {sed} {file}"
        return self.adapter.ssh_call(cmd)

    async def __add_dhcphost(self, vmid: int, adr: str):
        """Adds the desired dns host in the dnsmasq config"""
        file = f"{self.config.dnsmasqhosts}"
        line = (
            f"dhcp-host={self.config.prefixmac}:{vmid:x},id:" f",daas-{vmid},{adr},1m"
        )
        cmd = f"echo {line} | tee -a {file} > /dev/null"
        return self.adapter.ssh_call(cmd)
