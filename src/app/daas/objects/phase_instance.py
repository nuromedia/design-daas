"""Baseclass for a virtualized object using Guacamole."""

import os
from dataclasses import dataclass
from app.daas.common.enums import BackendName
from app.daas.objects.base_instance import InstanceObjectBase

# from app.daas.objects.object_container import ContainerObject
# from app.daas.objects.object_machine import MachineObject
from app.daas.storage.filestore import Filestore
from app.qweb.common.qweb_tools import get_backend_component
from app.qweb.processing.processor import QwebResult


DEFAULT_TIMEOUTS = 3


@dataclass(kw_only=True)
class InstancePhase(InstanceObjectBase):
    """Configuration for a virtualized object using Guacamole."""

    async def inst_vminvoke_app(self, cmd: str, args: str) -> QwebResult:
        """Invokes a (non-blocking) app command"""
        return await self._run_inst("app", cmd, args)

    async def inst_vminvoke_cmd(self, cmd: str, args: str) -> QwebResult:
        """Invokes a (blocking) cmd command"""
        return await self._run_inst("cmd", cmd, args)

    async def inst_vminvoke_ssh(self, cmd: str, args: str) -> QwebResult:
        """Invokes raw ssh command"""
        return await self._run_ssh(cmd, args)

    async def inst_vminvoke_action(self, cmd: str, args: str) -> QwebResult:
        """Invokes a (blocking) action command"""
        return await self._run_inst("action", cmd, args)

    async def inst_vminvoke_resolution(self, cmd: str, args: str) -> QwebResult:
        """Invokes a (blocking) resolution command"""
        return await self._run_inst("resolution", cmd, args)

    async def inst_vminvoke_ospackage(self, cmd: str, args: str) -> QwebResult:
        """Invokes a (blocking) ospackage command"""
        return await self._run_inst("ospackage", cmd, args)

    async def inst_vminvoke_upload(
        self, src: str, win: bool, run: bool, filename: str = ""
    ) -> QwebResult:
        """Invokes a (blocking) upload command"""
        store = await get_backend_component(BackendName.FILE, Filestore)
        win = await self.needs_pstools()
        dst = await store.get_filename_instance(src, win, "tmp")
        path = os.path.dirname(dst)
        if filename != "":
            dst = f"{path}/{filename}"
        if win:
            await self._run_ssh("mkdir", f'"{path}"')
        else:
            await self._run_ssh("mkdir", f"-p {path}")

        uploaded = await self._run_upload(src, dst)
        if run:
            if win:
                return await self._run_inst("cmd", dst, "")
            else:
                await self._run_ssh("/usr/bin/chmod", f"a+x {dst}")
                return await self._run_inst("cmd", "/usr/bin/xterm", f"-e {dst}")

        return uploaded

    async def inst_vminvoke_filesystem(
        self, cmd: str, cpub: bool, cshared: bool, cuser: bool
    ) -> QwebResult:
        """Invokes a (blocking) filesystem command"""
        raise NotImplementedError()

    async def inst_vminvoke_test_icmp(self) -> QwebResult:
        """Invokes a (blocking) icmp test command (ping)"""
        code, msg, err = await self._run_test_icmp(self.host, DEFAULT_TIMEOUTS)
        if code == 0:
            return QwebResult(200, {}, 0, f"{msg}{err}")
        return QwebResult(400, {}, 1, "Error on invoke_test_icmp()")

    async def inst_vminvoke_test_ssh(self) -> QwebResult:
        """Invokes a (blocking) ssh test command"""
        code, msg, err = await self._run_test_ssh(self.host, DEFAULT_TIMEOUTS)
        if code == 0:
            return QwebResult(200, {}, 0, f"{msg}{err}")
        return QwebResult(400, {}, 1, "Error on invoke_test_ssh()")

    async def inst_vminvoke_rtt(self) -> QwebResult:
        """Invokes a (blocking) ssh test command"""
        raise NotImplementedError()

    async def _run_upload(self, src: str, dst: str) -> QwebResult:
        code, msg, err = await self._invoke_scp_upload(self.host, src, dst)
        if code == 0:
            return QwebResult(200, {}, 0, f"{msg}{err}")
        return QwebResult(400, {}, 1, "Error on invoke_upload()")

    async def _run_inst(self, ctype: str, cmd: str, args: str) -> QwebResult:
        strargs = f"{cmd} {args}"
        pstools = await self.needs_pstools()
        code, msg, err = await self._invoke_instance(self.host, ctype, strargs, pstools)
        if code == 0:
            return QwebResult(200, {}, 0, f"{msg}{err}")
        return QwebResult(400, {}, 1, "Error on invoke_inst()")

    async def _run_ssh(self, cmd: str, args: str) -> QwebResult:
        code, msg, err = await self._invoke_raw_ssh(self.host, cmd, args)
        if code == 0:
            return QwebResult(200, {}, 0, f"{msg}{err}")
        return QwebResult(400, {}, 1, "Error on invoke_ssh()")

    # async def inst_vmstatus(self, adr: str):
    #     """Invoke a status action via client api"""
    #     return await self._invoke_instance(adr, "status", "", False)
    #
    # async def inst_vmversion(self, adr: str):
    #     """Invoke a version action via client api"""
    #     return await self._invoke_instance(adr, "version", "", False)
    #
    # async def inst_vminvoke_fs(
    #     self, adr: str, cmd: str, args: list[str], pstools: bool
    # ) -> tuple[int, str, str]:
    #     """Filesystem command"""
    #     code, str_out, str_err = await self._invoke_filesystem_cmd(
    #         adr, cmd, args, pstools
    #     )
    #     return code, str_out, str_err
    #
