"""
Proxies control backend to instance
"""

import os
import logging
from dataclasses import dataclass

from adapter.AdapterBase import AdapterBaseConfig

# ProxyControl defaults
DEFAULT_LOGNAME = "CommandProxy.py"
DEFAULT_DATALOG = "Datalogger"

# ProxyControl defaults
DEFAULT_FILESYSTEMCMD_ALLOWED = ["mount", "unmount"]
DEFAULT_PACKAGECMD_ALLOWED = ["install", "uninstall"]
DEFAULT_RESOLUTIONCMD_ALLOWED = ["get", "set", "list", "pstools"]
DEFAULT_ACTIONS_ALLOWED = ["status", "version", "ping", "rtt", "tasklist"]
DEFAULT_PROGRAMS_DISABLED = [""]
DEFAULT_APPS_DISABLED = [""]

# AdapterBase default
PROXY_VERSION = "0.6.2"
DEFAULT_RESOLUTION = (640, 480)

# Linux defaults
NIXCFG_DEFAULT_MONITOR_VM = "Virtual-1"
NIXCFG_DEFAULT_MONITOR_DOCKER = "VNC-0"
NIXCFG_OSPACKAGE_TOOL = "/usr/bin/apt"

# Windows defaults
WINCFG_USER = "root"
WINCFG_CODEPAGE = "cp850"
WINCFG_PIDSEARCH_TIMEOUT = 5
WINCFG_MAPPING_UWP = {
    "calc.exe": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
}
WINCFG_FILENAME_TIGHTVNC = "C:/Program Files/TightVNC/tvnserver.exe"
WINCFG_OSPACKAGE_TOOL = "winget"


# Conditional imports
if os.name == "posix":
    from adapter.LinuxAdapter import LinuxAdapter
    from adapter.LinuxAdapter import LinuxAdapterConfig

elif os.name == "nt":
    from adapter.WindowsAdapter import WindowsAdapter
    from adapter.WindowsAdapter import WindowsAdapterConfig


@dataclass
class ProxyControlMappings:
    """
    Mappings to limit ProxyControl access
    """

    packagecmd_allowed: list
    filesystemcmd_allowed: list
    resolutioncmd_allowed: list
    actions_allowed: list
    apps_disabled: list
    cmd_disabled: list


class ProxyControl:
    """
    Proxy component to execute commands
    within virtualized or containerized instances
    """

    def __init__(self):
        """
        Default constructor
        """
        self.cfg = ProxyControlMappings(
            DEFAULT_PACKAGECMD_ALLOWED,
            DEFAULT_FILESYSTEMCMD_ALLOWED,
            DEFAULT_RESOLUTIONCMD_ALLOWED,
            DEFAULT_ACTIONS_ALLOWED,
            DEFAULT_PROGRAMS_DISABLED,
            DEFAULT_APPS_DISABLED,
        )
        self.__init_logging()
        self.adapter = self.__get_os_adapter()

    def execute_app(self, prog: str, args: list) -> tuple:
        """
        Executes specified app
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_app(prog, args)
        if code != 0:
            self.__log_error(txt_err)
            return code, "", txterr
        result, txt_out, txt_err = self.adapter.spawn_app(prog, args)
        self.__log_data(f"{txt_out}{txt_err}")
        return result, txt_out, txt_err

    def execute_cmd(self, prog: str, args: list) -> tuple:
        """
        Executes specified command line
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_cmd(prog, args)
        if code != 0:
            self.__log_error(txt_err)
            return code, "", txterr
        result, txt_out, txt_err = self.adapter.spawn_process(prog, args)
        self.__log_data(f"{txt_out}{txt_err}")
        return result, txt_out, txt_err

    def execute_action(self, action_type: str, args: list) -> tuple:
        """
        Executes specified action
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_action(action_type, args)
        if code != 0:
            return code, "", txterr
        if action_type == "status":
            result, txt_out, txt_err = self.adapter.action_status()
        elif action_type == "version":
            result, txt_out, txt_err = self.adapter.action_version()
        elif action_type == "ping":
            result, txt_out, txt_err = self.adapter.action_ping(args)
        elif action_type == "rtt":
            result, txt_out, txt_err = self.adapter.action_rtt(args)
        elif action_type == "tasklist":
            result, txt_out, txt_err = self.adapter.tasklist_get(args)
        self.__log_data(txt_out)
        return result, txt_out, txt_err

    def execute_resolution(self, resolution_cmd: str, args: list) -> tuple:
        """
        Performs a resize by utilizing native os facilities
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_resolution(resolution_cmd, args)
        if code != 0:
            return code, "", txterr
        if resolution_cmd == "get":
            width, height = self.adapter.resolution_get(args)
            result = 0
            txt_out = f"{width}x{height}"
        elif resolution_cmd == "list":
            result, txt_out, txt_err = self.adapter.resolution_list(args)
        elif resolution_cmd == "set":
            result, txt_out, txt_err = self.adapter.resolution_set(args)
        self.__log_data(txt_out)
        return result, txt_out, txt_err

    def execute_ospackage(self, package_cmd: str, args: list) -> tuple:
        """
        Performs a resize by utilizing native os facilities
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_ospackage(package_cmd, args)
        if code != 0:
            return code, "", txterr
        if package_cmd == "install":
            result, txt_out, txt_err = self.adapter.ospackage_install(args)
        elif package_cmd == "uninstall":
            result, txt_out, txt_err = self.adapter.ospackage_uninstall(args)
        self.__log_data(txt_out)
        return result, txt_out, txt_err

    def execute_filesystem(self, package_cmd: str, args: list) -> tuple:
        """
        Performs a filesystem operation
        """
        result = -1
        txt_out = ""
        txt_err = ""
        code, txterr = self.check_filesystem(package_cmd, args)
        if code != 0:
            return code, "", txterr
        if package_cmd == "mount":
            result, txt_out, txt_err = self.adapter.filesystem_mount(args)
        elif package_cmd == "unmount":
            result, txt_out, txt_err = self.adapter.filesystem_unmount(args)
        self.__log_data(txt_out)
        return result, txt_out, txt_err

    def check_app(self, check_type: str, args: list) -> tuple:
        """
        Checks if app command is valid
        """
        if check_type in self.cfg.apps_disabled:
            txt_err = f"Disabled app command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def check_cmd(self, check_type: str, args: list) -> tuple:
        """
        Checks if cmd command is valid
        """
        if check_type in self.cfg.cmd_disabled:
            txt_err = f"Disabled cmd command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def check_action(self, check_type: str, args: list) -> tuple:
        """
        Checks if action command is valid
        """
        if check_type not in self.cfg.actions_allowed:
            txt_err = f"Unknown action command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def check_resolution(self, check_type: str, args: list) -> tuple:
        """
        Checks if resolution command is valid
        """
        if check_type not in self.cfg.resolutioncmd_allowed:
            txt_err = f"Unknown resolution command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def check_ospackage(self, check_type: str, args: list) -> tuple:
        """
        Checks if ospackage command is valid
        """
        if check_type not in self.cfg.packagecmd_allowed:
            txt_err = f"Unknown package command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def check_filesystem(self, check_type: str, args: list) -> tuple:
        """
        Checks if filesystem command is valid
        """
        if check_type not in self.cfg.filesystemcmd_allowed:
            txt_err = f"Unknown filesystem command: {check_type} {args}"
            self.__log_error(txt_err)
            return 1, txt_err
        return 0, ""

    def __get_os_adapter(self):
        """
        Retrieves CommandProxy based on currently used operating system
        """
        baseconf = AdapterBaseConfig(PROXY_VERSION, DEFAULT_LOGNAME, DEFAULT_RESOLUTION)
        if os.name == "posix":
            isvm = False
            mon = NIXCFG_DEFAULT_MONITOR_VM
            if os.path.exists("/.dockerenv"):
                isvm = True
                mon = NIXCFG_DEFAULT_MONITOR_DOCKER
            nixcfg = LinuxAdapterConfig(isvm, mon, NIXCFG_OSPACKAGE_TOOL)
            return LinuxAdapter(baseconf, nixcfg)
        if os.name == "nt":
            wincfg = WindowsAdapterConfig(
                True,
                WINCFG_USER,
                WINCFG_CODEPAGE,
                WINCFG_PIDSEARCH_TIMEOUT,
                WINCFG_MAPPING_UWP,
                WINCFG_FILENAME_TIGHTVNC,
                WINCFG_OSPACKAGE_TOOL,
            )
            return WindowsAdapter(baseconf, wincfg)
        raise NotImplementedError()

    def __log_data(self, msg: str):
        print(msg, end="")

    def __log_error(self, msg: str):
        logging.getLogger(DEFAULT_LOGNAME).error(msg)

    def __init_logging(self):
        logging.basicConfig(
            format="%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
            level=logging.DEBUG,
            handlers=[logging.StreamHandler()],
        )
