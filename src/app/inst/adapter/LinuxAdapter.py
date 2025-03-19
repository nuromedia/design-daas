"""
LinuxAdapter
"""
from dataclasses import dataclass

from .tools.LinuxTools import (
    get_process_list,
    process_kill,
    process_popen,
    process_run,
    choose_valid_resolution_linux,
    extract_current_resolution,
    extract_resolutions,
    resolution_set,
    get_monitor_from_args,
    get_ospackage_args,
    try_find_pid,
    persist_pid,
)

from adapter.AdapterBase import AdapterBase, AdapterBaseConfig


@dataclass
class LinuxAdapterConfig:
    """
    Represents initial config values for the LinuxAdapter
    """

    is_vm: bool
    default_monitor: str
    ospackage_tool: str


class LinuxAdapter(AdapterBase):
    """
    Linux implementation for CommandProxy
    """

    def __init__(self, baseconf: AdapterBaseConfig, conf: LinuxAdapterConfig):
        super().__init__(baseconf)
        self.cfg = conf

    def spawn_app(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns an app within Linux
        """

        oldpid = try_find_pid(prog)
        if oldpid > 0:
            process_kill(oldpid)

        pid = process_popen(prog, args)
        if pid > 0:
            persist_pid(pid)
            return 0, f"{pid}", ""
        return -1, "", f"Error on spawning app: {prog}"

    def spawn_process(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns a process within Linux
        """
        code, str_out, str_err = process_run(prog, args)
        if code == 0:
            return code, str_out, str_err
        return -1, str_out, f"Error on spawning cmd: {prog}\n{str_err}"

    def ospackage_install(self, args: list) -> tuple[int, str, str]:
        """
        Installs package by using native os facilities
        """
        if len(args) == 1:
            return self.spawn_process(
                self.cfg.ospackage_tool,
                args=get_ospackage_args(True, args[0]),
            )
        return (-1, "", f"Argument size invalid: {len(args)}")

    def ospackage_uninstall(self, args: list) -> tuple[int, str, str]:
        """
        Uninstalls by using native os facilities
        """
        if len(args) == 1:
            return self.spawn_process(
                self.cfg.ospackage_tool,
                args=get_ospackage_args(False, args[0]),
            )
        return (-1, "", f"Argument size invalid: {len(args)}")

    def resolution_get(self, args: list) -> tuple:
        """
        Gets current screen resolution by using native os facilities
        """
        mon = get_monitor_from_args(args, self.cfg.default_monitor)
        return extract_current_resolution(mon)

    def resolution_set(self, args: list) -> tuple[int, str, str]:
        """
        Sets current screen resolution by using native os facilities
        Defaults to 640x480
        """
        default_width, default_height = self.get_default_resolution()

        width, height = self.split_dimensions(args)

        width, height = choose_valid_resolution_linux(
            self.cfg.default_monitor,
            width,
            height,
            default_width,
            default_height,
        )
        code, str_out, str_err = resolution_set(
            width, height, self.cfg.default_monitor
        )
        if code == 0:
            return code, f"{width}x{height}", ""
        return code, str_out, str_err

    def tasklist_get(self, args: list) -> tuple[int, str, str]:
        """
        Enumerates running processes
        """
        procfilter = " ".join(args)
        tasklist = get_process_list(procfilter)
        return 0, f"{tasklist}", ""

    def resolution_list(self, args: list) -> tuple[int, str, str]:
        """
        Enumerates available screen resolutions by using native os facilities
        """
        mon = get_monitor_from_args(args, self.cfg.default_monitor)
        resolutions = extract_resolutions(mon)
        return 0, f"{resolutions}", ""

    def filesystem_mount(self, args: list) -> tuple[int, str, str]:
        """
        Mount filesystem
        """
        if len(args) == 4:
            user = args[0]
            cephdir = args[1]
            localdir = args[2]
            fsname = args[3]
            key_file = f"/etc/ceph/ceph.{user}.keyring"
            mount_args: list[str] = [
                "-p",
                localdir,
                ";",
                "ceph-fuse",
                localdir,
                "-n",
                user,
                "-r",
                cephdir,
                "-k",
                key_file,
                f"--client-fs={fsname}",
            ]
            code = process_popen("mkdir", mount_args)
            if code != 0:
                return code, "", "Error on mount"
        else:
            return 1, "", f"Invalid argumentlist size {len(args)}. Expected 4"
        return 0, "", ""

    def filesystem_unmount(self, args: list) -> tuple[int, str, str]:
        """
        Unmount filesystem
        """
        if len(args) == 1:
            localdir = args[0]
            code = process_popen("fusermount", ["-u", localdir])
            if code != 0:
                return code, "", "Error on unmount"
        else:
            return 1, "", f"Invalid argumentlist size {len(args)}. Expected 1"
        return 0, "", ""
