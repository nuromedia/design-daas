"""Baseclass for ObjectInstance"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from nest_asyncio import asyncio
from quart.utils import run_sync
from app.daas.adapter.adapter_ssh import SshAdapter, SshAdapterConfig
from app.daas.common.enums import BackendName
from app.daas.common.model import GuacamoleConnection, Instance
from app.daas.messaging.qmsg.common.qmsg_model import RpcRequest, RpcResponse
from app.daas.messaging.qmsg.hub_backend import QHubBackend
from app.plugins.platform.messaging.messaging_backend import MessagingBackend
from app.qweb.common.qweb_tools import get_backend, get_backend_component, get_database
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass(kw_only=True)
class InstanceObjectBase(Instance):
    """Baseclass for ObjectInstance"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Loggable.__init__(self, LogTarget.INST)

    async def create_adapter_local(self) -> SshAdapter:
        """Create Adapter for a specific instance"""
        hub = await get_backend(BackendName.MESSAGING, MessagingBackend)
        return SshAdapter(hub.cfg_ssh)

    async def create_adapter(self, adr: str) -> SshAdapter:
        """Create Adapter for a specific instance"""
        hub = await get_backend(BackendName.MESSAGING, MessagingBackend)
        cfg = SshAdapterConfig(
            hub.cfg_main.sshuser,
            adr,
            hub.cfg_main.sshport,
            hub.cfg_main.sshopt_timeout,
            hub.cfg_main.sshopt_strictcheck,
            hub.cfg_main.sshopt_nohostauth,
            hub.cfg_main.logcmd,
            hub.cfg_main.logresult,
        )
        return SshAdapter(cfg)

    async def needs_pstools(self):
        result = False
        # qmsg = await self.get_backend()
        # if qmsg.cfg_main.enable_message_queue is False:
        if self.app.os_type in ("win10", "win11"):
            result = True
        return result

    async def get_backend(self) -> MessagingBackend:
        return await get_backend(BackendName.MESSAGING, MessagingBackend)

    async def get_connection_info(self) -> dict:
        con = await self._get_connection()
        return {
            "object": self.app.id,
            "name": self.app.id_user,
            "env": self.env,
            "instance": self.id,
            "viewer_url": con.viewer_url if con is not None else "",
        }

    async def check_online_state(self) -> bool:
        qmsg = await self.get_backend()
        method = qmsg.cfg_main.test_method_online_state
        if method == "queue":
            online = qmsg.component.heartbeat_receiver.is_online(self.host)
            if online:
                self._log_info(f"Instance is ONLINE: {self.id}", 0)
            else:
                self._log_info(f"Instance is OFFLINE: {self.id} {self.host}", 1)
            return online
        elif method == "icmp":
            code, _, _ = await self._run_test_icmp(self.host, 1)
            return code == 0
        else:
            self._log_error(f"Unknown test method: {method}", 1)
        return False

    async def _invoke_instance(
        self,
        adr: str,
        invocation_type: str,
        args: str,
        pstools: bool,
    ) -> tuple[int, str, str]:
        hub = await get_backend(BackendName.MESSAGING, MessagingBackend)
        if hub.cfg_main.enable_message_queue is False:
            return await self._invoke_instance_ssh(adr, invocation_type, args, pstools)
        return await self._invoke_instance_queue(adr, invocation_type, args, pstools)

    async def _invoke_raw_ssh(
        self,
        adr: str,
        cmd: str,
        args: str,
    ) -> tuple[int, str, str]:
        return await self._invoke_ssh_cmd(adr, cmd, args.split(" "))

    async def _invoke_instance_ssh(
        self, adr: str, invocation_type: str, args: str, pstools: bool
    ) -> tuple[int, str, str]:
        """
        Invoke client api
        """
        session = 1
        if pstools:
            code, user_sessions, _ = await self._invoke_ssh_cmd(adr, "query user", [])
            if code == 0:
                arr = user_sessions.split()
                if len(arr) == 13:
                    session = int(arr[8])
            cmd = await self._get_commandline_pstools(session, "root", "root")
            client_args = [
                "pythonw",
                "C:/Users/root/daas/env/CommandProxy.py",
                invocation_type,
            ]
            client_args.extend(args.split())
        else:
            cmd = "python3"
            client_args = [
                "/root/daas/env/CommandProxy.py",
                invocation_type,
            ]
            client_args.extend(args.split())
        code, str_out, str_err = await self._invoke_ssh_cmd(adr, cmd, client_args)
        return code, str_out, str_err

    async def _invoke_instance_queue(
        self, adr: str, invocation_type: str, args: str, pstools: bool, timeout: int = 0
    ) -> tuple[int, str, str]:
        """
        Invoke client api
        """
        hub = await get_backend_component(BackendName.MESSAGING, QHubBackend)
        cmd = ""
        client_args = []
        arr = args.split(" ")
        if len(args) > 0:
            cmd = arr[0]
            if len(args) > 1:
                client_args = arr[1:]
        if pstools:
            is_online = hub.heartbeat_receiver.is_online(adr)
            if is_online is None:
                return -1, "", f"Host is offline: {adr}"
            req = RpcRequest(
                datetime.now().timestamp(),
                "backend",
                hub.ip_address,
                invocation_type,
                cmd,
                client_args,
            )
            ts_start = datetime.now().timestamp()
            response: Optional[RpcResponse] = await run_sync(hub.call_rpc)(adr, req)
            ts_stop = datetime.now().timestamp()
            ts_diff = ts_stop - ts_start
            if response is None:
                return -1, "", "msg request failed"
            code = response.processor_result["code"]
            str_out = response.processor_result["std_out"]
            str_err = response.processor_result["std_err"]
            await self.__log_request(cmd, client_args, code, str_out, str_err, ts_diff)
            return (code, str_out, str_err)
        is_online = hub.heartbeat_receiver.is_online(adr)
        if is_online is False:
            return -1, "", "No heartbeat"

        req = RpcRequest(
            datetime.now().timestamp(),
            "backend",
            hub.ip_address,
            invocation_type,
            cmd,
            client_args,
        )
        response: Optional[RpcResponse] = await run_sync(hub.call_rpc)(adr, req)
        if response is None:
            return -1, "", "msg request failed"

        ts_start = response.timestamp
        ts_stop = datetime.now().timestamp()
        ts_diff = ts_stop - ts_start
        code = response.processor_result["code"]
        str_out = response.processor_result["std_out"]
        str_err = response.processor_result["std_err"]
        # await self.__log_request(cmd, client_args, code, str_out, str_err, ts_diff)
        return (code, str_out, str_err)

    async def _get_commandline_pstools(self, session: int, user: str, password: str):
        return (
            "C:/Users/root/daas/env/pstools/psexec.exe"
            " -nobanner -accepteula"
            f" -i {session} -u {user} -p {password}"
        )

    async def _invoke_ssh_cmd(
        self, adr: str, cmd: str, args: list[str]
    ) -> tuple[int, str, str]:
        """Invoke a command line via ssh"""

        if adr in ("", "unassigned"):
            self._log_error(f"Error! ip not valid: {adr}")
            raise ValueError(f"The supplied ip was not valid : {adr}")

        joined_cmd = f"{cmd} " + " ".join(args)
        adapter = await self.create_adapter(adr)
        ts_start = datetime.now().timestamp()
        code, str_out, str_err = await run_sync(adapter.ssh_call)(joined_cmd)
        ts_stop = datetime.now().timestamp()
        ts_diff = ts_stop - ts_start
        await self.__log_request(cmd, args, code, str_out, str_err, ts_diff)
        return code, str_out, str_err

    async def _invoke_scp_upload(
        self, adr: str, src: str, dst: str
    ) -> tuple[int, str, str]:
        """Invoke a command line via ssh"""
        adapter = await self.create_adapter(adr)
        # self._log_info(f"SCP UPLOAD: {adapter} -> {adr}")
        code, str_out, str_err = await run_sync(adapter.scp_upload_call)(src, dst)
        return code, str_out, str_err

    async def _invoke_local_cmd(
        self, cmd: str, args: list[str]
    ) -> tuple[int, str, str]:
        """Invoke a command line locally via ssh"""
        cmd = f"{cmd} " + " ".join(args)
        adapter = await self.create_adapter_local()
        ts_start = datetime.now().timestamp()
        code, str_out, str_err = await run_sync(adapter.ssh_call)(cmd)
        ts_stop = datetime.now().timestamp()
        ts_diff = ts_stop - ts_start
        await self.__log_request(cmd, args, code, str_out, str_err, ts_diff)
        return code, str_out, str_err

    async def _run_test_icmp(self, adr: str, timeout: int = 0) -> tuple[int, str, str]:
        args = ["-c1", "-W1", f"{adr}"]
        code = 1
        std_out = ""
        std_err = ""
        while timeout > 0:
            timeout -= 1
            code, std_out, std_err = await self._invoke_local_cmd("ping", args)
            checked = await self._check_ping_response(code, std_out)
            if checked is True:
                break
            else:
                code = 1
            await asyncio.sleep(0)
        return code, std_out, std_err

    async def _run_test_ssh(self, adr: str, timeout: int = 0) -> tuple[int, str, str]:
        code = 1
        std_out = ""
        std_err = ""
        while timeout > 0:
            timeout -= 1
            code, std_out, std_err = await self._invoke_raw_ssh(adr, "cmd", "cd")
            if code == 0:
                break
            await asyncio.sleep(0)
        return code, std_out, std_err

    async def _check_ping_response(self, code: int, stdout: str) -> bool:
        """Checks ping response for success"""
        result = False
        if code == 0:
            if stdout != "" and stdout.find("100% packet loss") == -1:
                self._log_info("Instance is ONLINE", 0)
                result = True
            else:
                self._log_info("Instance is OFFLINE", 1)
        return result

    async def _get_connection(self) -> Optional[GuacamoleConnection]:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if self.id_con is not None:
            return await dbase.get_guacamole_connection(self.id_con)
        return None

    async def _get_contype_from_object_mode(self) -> str:
        from app.daas.objects.base_object import DaasBaseObject

        if isinstance(self.app, DaasBaseObject):
            if self.app.is_machine():
                if self.app.object_mode in ("run-app"):
                    return self.app.viewer_contype
                return "sysvnc"
            else:
                if self.app.object_mode in ("run-app"):
                    return self.app.viewer_contype
                return "instvnc"
        return ""

    async def __log_request(
        self, cmd: str, args: list, code: int, str_out: str, str_err: str, diff_s: float
    ):
        hub = await get_backend(BackendName.MESSAGING, MessagingBackend)
        header = "INST-S:"
        if hub.cfg_main.enable_message_queue:
            header = "INST-R:"
        msg = f"{header} {code:3} -> {diff_s*1000:7.1f}ms CMD={cmd},ARGS={args}"
        if hub.cfg_main.logresult:
            if str_out.endswith("\n"):
                str_out = str_out[:-1]
            if str_err.endswith("\n"):
                str_err = str_err[:-1]
            msg = msg + f" RESULT: {str_out}{str_err}"
        self._log_info(msg)

    #
    # async def _invoke_filesystem_cmd(
    #     self, adr: str, invocation_type: str, args: list[str], pstools: bool
    # ) -> tuple[int, str, str]:
    #     if pstools:
    #         cmd = "C:/Users/root/daas/env/pstools/psexec.exe"
    #         # cmd = "python"
    #         client_args = [
    #             " -nobanner",
    #             "-accepteula",
    #             "-i",
    #             "1",
    #             "-u",
    #             "root",
    #             "-p",
    #             "root",
    #             "cmd.exe",
    #             "/c",
    #             "start",
    #             "pythonw",
    #             "C:/Users/root/daas/env/CommandProxy.py",
    #             "filesystem",
    #             invocation_type,
    #         ]
    #         client_args.extend(args)
    #     else:
    #         cmd = "python3"
    #         client_args = [
    #             "/root/daas/env/CommandProxy.py",
    #             "filesystem",
    #             invocation_type,
    #         ]
    #         # if wine:
    #         #     client_args.append("wine")
    #         client_args.extend(args)
    #     return await self._invoke_ssh_cmd(adr, cmd, client_args)
    #
