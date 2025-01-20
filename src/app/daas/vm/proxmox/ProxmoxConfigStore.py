from dataclasses import dataclass

from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class ProxmoxConfigStoreConfig:
    """
    Config for ConfigStore
    """

    storage_iso: str
    storage_img: str
    storage_ceph: str
    bridge_name_daas: str
    prefixmac: str


class ProxmoxConfigStore(Loggable):
    """
    Provides configuration presets for proxmox vms
    """

    def __init__(self, cfg_store: ProxmoxConfigStoreConfig):
        Loggable.__init__(self, LogTarget.VM)
        self.cfg = cfg_store
        self.options_iso = "media=cdrom,size=5992742K"
        self.options_disk = "format=qcow2,cache=writethrough,iothread=1"

    def create_vmconf_installation(
        self,
        *,
        vmid: int,
        name: str,
        ostype: str,
        cores: int,
        memsize: int,
        disksize: int,
        ceph_pool: bool,
        iso_installer: str,
        keyboard_layout: str,
    ) -> dict:
        """
        Provides a configuration preset for installation based on ostype.

        Ostype can be one of `l26` (debian), `win10`, `win11`
        """
        # check for unsupported ostype
        if ostype in ("win10", "win11"):

            def select_for_os(*, windows, debian):
                # pylint: disable=unused-argument
                return windows

        elif ostype in ("l26", "l26vm"):

            def select_for_os(*, windows, debian):
                # pylint: disable=unused-argument
                return debian

        else:
            return {}

        mac = f"{self.cfg.prefixmac}:{vmid:x}"
        iso2 = f"{self.cfg.storage_iso}:iso/{iso_installer},{self.options_iso}"
        if ceph_pool:
            disk0 = f"{self.cfg.storage_ceph}:{disksize},{self.options_disk}"
        else:
            disk0 = f"{self.cfg.storage_img}:{disksize},{self.options_disk}"

        disk_debian = {
            "ide2": iso2,
            "virtio0": disk0,
            "scsihw": "virtio-scsi-single",
            "boot": "order=virtio0;ide2",
        }

        disk_windows = {
            "sata2": iso2,
            "virtio0": disk0,
            "scsihw": "virtio-scsi-pci",
            "boot": "order=virtio0;sata2;",
        }

        return {
            "vmid": vmid,
            "name": name,
            "agent": 1,
            "numa": 1,
            "balloon": select_for_os(windows=1, debian=0),
            "reboot": 1,
            "kvm": 1,
            "cores": cores,
            "sockets": 1,
            "memory": memsize,
            "ostype": ostype,
            "machine": "pc-q35-8.0",
            "net0": f"virtio={mac},bridge={self.cfg.bridge_name_daas}",
            **select_for_os(windows=disk_windows, debian=disk_debian),
            "args": f"-k {keyboard_layout} -vnc 0.0.0.0:{vmid},password=on",
        }

    def create_vmconf_baseimage(self, vmid: int, name: str, keyboard: str) -> dict:
        """
        Provides a generic configuration preset to initialize baseimages
        """
        mac = f"{self.cfg.prefixmac}:{vmid:x}"
        return {
            "name": name,
            "boot": "order=virtio0;",
            "ide2": "file=none",
            "sata2": "file=none",
            # "net0": "",
            "delete": "net0",
            "net1": f"virtio={mac},bridge={self.cfg.bridge_name_daas}",
            "args": f"-k {keyboard} -vnc 0.0.0.0:{vmid},password=on",
        }

    def create_vmconf_template(self, vmid: int, name: str, keyboard: str) -> dict:
        """
        Provides a generic configuration preset to initialize object templates
        """
        return {
            "name": name,
            "boot": "order=virtio0;",
            "ide2": "file=none",
            "sata2": "file=none",
            "delete": "net0,net1",
            "args": f"-k {keyboard} -vnc 0.0.0.0:{vmid},password=on",
        }
