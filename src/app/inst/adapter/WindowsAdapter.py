"""
Windowsbase
"""

import time
from dataclasses import dataclass
from adapter.AdapterBase import AdapterBase, AdapterBaseConfig


from .tools.WindowsTools import (
    try_find_pid,
    process_popen,
    process_run,
    clean_session,
    get_resolution_list,
    get_resolution_by_dimension,
    get_process_list,
    persist_pid,
    tightvnc_update,
    maximize_windows_by_pid,
    generate_searchterms,
    process_kill,
    get_current_resolution,
    set_current_resolution,
    construct_ospackage_arguments,
)

# Globals
CEPH_BIANRY = "ceph-dokan"


@dataclass
class WindowsAdapterConfig:
    """
    Represents initial config values for the WindowsAdapter
    """

    is_vm: bool
    user: str
    codepage: str
    timeout_pidsearch: int
    mapping_uwp: dict
    filename_tightvnc: str
    ospackage_tool: str


class WindowsAdapter(AdapterBase):
    """
    Windows implementation for CommandProxy
    """

    def __init__(self, baseconf: AdapterBaseConfig, conf: WindowsAdapterConfig):
        """
        Sets initial config with default values
        """
        super().__init__(baseconf)
        self.cfg = conf

    def spawn_app(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns an app within Windows
        """
        # clean_session(self.cfg.codepage)
        terms = generate_searchterms(prog, self.cfg.mapping_uwp)
        pid = try_find_pid(terms, self.cfg.timeout_pidsearch)
        if pid != -1:
            process_kill(pid, self.cfg.codepage)

        code = process_popen(prog, args, False, self.cfg.codepage)
        pid = try_find_pid(terms, self.cfg.timeout_pidsearch)
        if pid != -1:
            persist_pid(pid, self.cfg.user)
            tightvnc_update(pid, self.cfg.filename_tightvnc, self.cfg.codepage)
            maximize_windows_by_pid(pid, terms)
        else:
            pid = try_find_pid(terms, self.cfg.timeout_pidsearch)
            if pid != -1:
                persist_pid(pid, self.cfg.user)
                tightvnc_update(pid, self.cfg.filename_tightvnc, self.cfg.codepage)
                maximize_windows_by_pid(pid, terms)
        print(f"Spawned pid: {pid}")
        return code, f"{pid}", ""

    def spawn_process(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns a process within Windows
        """
        return process_run(prog, args, False, self.cfg.codepage)

    def ospackage_install(self, args: list) -> tuple[int, str, str]:
        """
        Installs package by using native os facilities
        """
        if len(args) == 1:
            winget_args = construct_ospackage_arguments(True, args[0])
            code, std_out, std_err = self.spawn_process(
                self.cfg.ospackage_tool, args=winget_args
            )
            return code, std_out, std_err
        return (-1, "", f"Argument size invalid: {len(args)}")

    def ospackage_uninstall(self, args: list) -> tuple[int, str, str]:
        """
        Uninstalls by using native os facilities
        """
        if len(args) == 1:
            winget_args = construct_ospackage_arguments(False, args[0])
            code, std_out, std_err = self.spawn_process(
                self.cfg.ospackage_tool, args=winget_args
            )
            return code, std_out, std_err
        return (-1, "", f"Argument size invalid: {len(args)}")

    def resolution_get(self, args: list) -> tuple:
        """
        Gets current screen resolution by using native os facilities
        """
        result = get_current_resolution(args)
        # clean_session("UTF-8")
        return result

    def resolution_list(self, args: list) -> tuple[int, str, str]:
        """
        Enumerates available screen resolutions by using native os facilities
        """
        reslist = get_resolution_list()
        # time.sleep(0.2)
        # clean_session("UTF-8")
        return 0, f"{reslist}", ""

    def resolution_set(self, args: list) -> tuple[int, str, str]:
        """
        Sets current screen resolution by using native os facilities
        """
        width, height = self.split_dimensions(args)
        width, height = get_resolution_by_dimension(width, height)
        if width == 0 or height == 0:
            width, height = self.get_default_resolution()
        set_current_resolution(width, height)
        # clean_session("UTF-8")
        return 0, f"{width}x{height}", ""

    def tasklist_get(self, args: list) -> tuple[int, str, str]:
        """
        Returns list of running processes
        """
        procfilter = " ".join(args)
        tasklist = get_process_list(procfilter)
        return 0, f"{tasklist}", ""

    def filesystem_mount(self, args: list) -> tuple[int, str, str]:
        """
        Mount filesystem
        """
        if len(args) == 4:
            clientid = args[0]
            cephdir = args[1]
            localdir = args[2]
            fsname = args[3]
            mount_args: list[str] = [
                "--name",
                clientid,
                "-x",
                cephdir,
                "-l",
                localdir,
                "--client_fs",
                fsname,
            ]
            code = process_popen(CEPH_BIANRY, mount_args, True, self.cfg.codepage)
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
            mount_args: list[str] = [
                "unmap",
                "-l",
                localdir,
            ]
            code = process_popen(CEPH_BIANRY, mount_args, True, self.cfg.codepage)
            if code != 0:
                return code, "", "Error on unmount"
        else:
            return 1, "", f"Invalid argumentlist size {len(args)}. Expected 1"
        return 0, "", ""
