"""
Adapterbase
"""

import os
import socket
import logging
from dataclasses import dataclass
from abc import abstractmethod, ABC
import time


@dataclass
class AdapterBaseConfig:
    """
    Represents initial config values for the AdapterBase
    """

    version: str
    logname: str
    default_resolution: tuple


class AdapterBase(ABC):
    """
    Abstract Base class for the Commandproxy
    """

    def __init__(self, conf: AdapterBaseConfig):
        self.baseconf = conf

    def action_status(self) -> tuple[int, str, str]:
        """
        Responds with a status message containing some basic host information
        """
        isvm = True
        if os.name == "posix":
            if os.path.exists("/.dockerenv") is False:
                isvm = True
        info = {
            "OS": f"{os.name}",
            "Host": f"{socket.gethostname()}",
            "Ip": f"{socket.gethostbyname(socket.getfqdn())}",
            "VM": f"{isvm}",
        }
        return (0, f"{info}", "")

    def split_dimensions(self, args: list) -> tuple:
        """
        Obtaines width and height from the argumentlist.

        Width and Height have to be seperated by an 'x'. As in '1920x1080'.
        Defaults to 640x480
        """
        width, height = self.get_default_resolution()

        if len(args) > 0 and "x" in args[0]:
            arr = args[0].split("x")
            width = int(arr[0])
            height = int(arr[1])
            return width, height
        msg = f"Could not parse params! Using defaults {width}x{height}"
        self.log_info(msg)
        return width, height

    def get_default_resolution(self):
        """
        Returns fallback resolution (640x480)
        """
        return (
            self.baseconf.default_resolution[0],
            self.baseconf.default_resolution[1],
        )

    def action_version(self) -> tuple[int, str, str]:
        """
        Responds with current version of the CommandProxy
        """
        return 0, f"{self.baseconf.version}", ""

    def action_rtt(self, args: list) -> tuple[int, str, str]:
        """
        Test method measuring roundtrip time (rtt)
        """
        begin_ms = int(args[0])

        joined = " ".join(args)
        now = int(time.time_ns() / 1000000)
        diff = now - begin_ms
        return 0, f"rtt {joined},{now},{diff}", ""

    def action_ping(self, args: list) -> tuple[int, str, str]:
        """
        Test method echoing the given arguments
        """
        joined = " ".join(args)
        return 0, f"pong {joined}", ""

    def log_info(self, msg: str):
        """
        Log info messages
        """
        logging.getLogger(self.baseconf.logname).info(msg)

    def log_error(self, msg: str):
        """
        Log error messages
        """
        logging.getLogger(self.baseconf.logname).error(msg)

    @abstractmethod
    def tasklist_get(self, args: list) -> tuple[int, str, str]:
        """
        Enumerates running processes
        """
        raise NotImplementedError()

    @abstractmethod
    def spawn_app(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns app with given arguments
        """
        raise NotImplementedError()

    @abstractmethod
    def spawn_process(self, prog: str, args: list) -> tuple[int, str, str]:
        """
        Spawns a new process with given arguments
        """
        raise NotImplementedError()

    @abstractmethod
    def resolution_get(self, args: list) -> tuple:
        """
        Gets current screen resolution by using native os facilities
        """
        raise NotImplementedError()

    @abstractmethod
    def resolution_list(self, args: list) -> tuple[int, str, str]:
        """
        Enumerates available screen resolutions by using native os facilities
        """
        raise NotImplementedError()

    @abstractmethod
    def resolution_set(self, args: list) -> tuple[int, str, str]:
        """
        Sets current screen resolution by using native os facilities
        """
        raise NotImplementedError()

    @abstractmethod
    def ospackage_install(self, args: list) -> tuple[int, str, str]:
        """
        Installs package by using native os facilities
        """
        raise NotImplementedError()

    @abstractmethod
    def ospackage_uninstall(self, args: list) -> tuple[int, str, str]:
        """
        Uninstalls by using native os facilities
        """
        raise NotImplementedError()

    @abstractmethod
    def filesystem_mount(self, args: list) -> tuple[int, str, str]:
        """
        Mount filesystem
        """
        raise NotImplementedError()

    @abstractmethod
    def filesystem_unmount(self, args: list) -> tuple[int, str, str]:
        """
        Unmount filesystem
        """
        raise NotImplementedError()
