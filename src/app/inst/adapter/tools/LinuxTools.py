"""
Linux helpers
"""
from dataclasses import dataclass
import subprocess
import logging
import re
import psutil


@dataclass
class Process:
    """
    Represents a process rerteived by tasklist
    """

    name: str
    cmdline: list[str]
    status: str
    pid: int
    username: str


def process_popen(prog: str, args: list) -> int:
    """
    Spawns a process within Linux
    """
    fullcmd = f"{prog} " + " ".join(args)
    subprocess.Popen(
        fullcmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    pid = try_find_pid(prog)
    if pid > 0:
        return pid
    return -1


def persist_pid(pid: int) -> tuple:
    """
    Persist pid into local file
    """
    cmd_mkdir = "/usr/bin/mkdir -p /root/daas/env/status"
    cmd_echo = f"echo {pid} > /root/daas/env/status/pid.txt"
    return process_run(f"{cmd_mkdir} ; {cmd_echo}", [])


def try_find_pid(prog: str) -> int:
    """
    Try to find pid by process name
    """
    result = -1
    grepparams = [
        "/usr/bin/ps aux",
        f"/usr/bin/grep {prog}",
        "/usr/bin/grep -Ev '(grep|python|/bin/sh -c)'",
        "/usr/bin/head -n1",
        "/usr/bin/tr -s ' '",
        "/usr/bin/cut -f2 -d' '",
    ]
    grepfilter = "|".join(grepparams)
    code, str_out, _ = process_run(grepfilter, [])
    if code == 0 and str_out != "":
        result = int(str_out)
    return result


def process_run(prog: str, args: list) -> tuple:
    """
    Spawns a process within Linux
    """
    fullcmd = f"{prog} " + " ".join(args)
    theproc = subprocess.run(
        fullcmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return theproc.returncode, theproc.stdout, theproc.stderr


def get_process_list(name: str = "") -> list:
    """
    Enumerates running processes
    """
    result = []
    for proc in psutil.process_iter():
        proc_element = None
        try:
            proc_element = Process(
                name=proc.name(),
                cmdline=proc.cmdline(),
                status=proc.status(),
                pid=proc.pid,
                username=proc.username(),
            )
        except psutil.AccessDenied:
            pass

        # Append if name is empty or euqal to proc.name
        if proc_element is not None:
            if name != "":
                if name == proc_element.name:
                    result.append(proc_element)
            else:
                result.append(proc_element)
    return result


def process_kill(killterm: int):
    """
    Kill process by given pid
    """
    try:
        kill_args = []
        if isinstance(killterm, int):
            kill_args = ["-9", f"{killterm}"]

        process_run("kill", kill_args)
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        OSError,
        FileNotFoundError,
        PermissionError,
        ValueError,
        UnicodeEncodeError,
        UnicodeDecodeError,
    ) as err:
        print(f"Exception during process kill: {err}")


def extract_resolutions(screen: str) -> list:
    """
    Extract all native resolutions
    """
    xrandr_output = subprocess.check_output("/usr/bin/xrandr").decode("utf-8")
    screen_pattern_open = re.compile(r'\b([\w-]+)\b(?=\s+connected\b)')
    screen_pattern_close = re.compile(r'\sdisconnected')
    resolution_pattern = re.compile(r'\s+(\d+)x(\d+)')

    result = []
    number = 0
    extracting = False
    lines = xrandr_output.split("\n")
    for line in lines:
        screen_match_close = screen_pattern_close.search(line)
        pattern_match = screen_pattern_open.search(line)
        if pattern_match:
            if pattern_match.group(0) == screen:
                # Found correct screen
                extracting = True
                continue
        if extracting:
            if screen_match_close:
                # Found another disconnected screen
                extracting = False
                break
            if pattern_match and pattern_match.group(0) != screen:
                # Found another connected screen
                extracting = False
                break
            resolution_match = resolution_pattern.search(line)
            if resolution_match:
                # Found resolution for correct screen
                result.append(
                    (
                        int(resolution_match.group(1)),
                        int(resolution_match.group(2)),
                    ),
                )
        number += 1
    return list(reversed(sorted(result)))


def get_ospackage_args(install: bool, name: str) -> list:
    """
    generates arguments foor ospackage install or uninstall calls
    """
    if install:
        return ["install", "-y", name]
    return ["remove", "-y", name]


def get_monitor_from_args(args: list, monitor: str) -> str:
    """
    Reads arguments and returns a default if empty
    """
    result = " ".join(args)
    if result == "":
        result = monitor
    return result


def resolution_set(width: int, height: int, monitor: str) -> tuple:
    """
    Sets new resolution
    """
    args = [
        "--output",
        monitor,
        "--mode",
        f"{width}x{height}",
    ]
    return process_run("/usr/bin/xrandr", args)


def extract_current_resolution(screen: str) -> tuple:
    """
    Extract current resolution
    """
    xrandr_output = subprocess.check_output("/usr/bin/xrandr").decode("utf-8")
    screen_pattern_open = re.compile(r'\b([\w-]+)\b(?=\s+connected\b)')
    screen_pattern_close = re.compile(r'\sdisconnected')
    resolution_pattern = re.compile(r'\s+(\d+)x(\d+)')

    number = 0
    extracting = False
    lines = xrandr_output.split("\n")
    for line in lines:
        screen_match_close = screen_pattern_close.search(line)
        pattern_match = screen_pattern_open.search(line)
        if pattern_match:
            if pattern_match.group(0) == screen:
                # Found correct screen
                # print(pattern_match.group(0))
                extracting = True
                continue
        if extracting:
            if screen_match_close:
                # Found another disconnected screen
                extracting = False
                break
            if pattern_match and pattern_match.group(0) != screen:
                # Found another connected screen
                extracting = False
                break
            resolution_match = resolution_pattern.search(line)
            if resolution_match and "*" in line:
                # Found resolution for correct screen
                return (
                    int(resolution_match.group(1)),
                    int(resolution_match.group(2)),
                )

        number += 1
    return -1, -1


def choose_valid_resolution_linux(
    screen: str,
    width: int,
    height: int,
    default_width: int,
    default_height: int,
) -> tuple:
    """
    Enumerates available screen resolution
    smaller or equal to the given width and height.

    Defaults to 640x480
    """
    resolutions = extract_resolutions(screen)
    if len(resolutions) > 0:
        for single in resolutions:
            # print(single)
            if width >= single[0] and height >= single[1]:
                return single[0], single[1]
    msg = f"No reasonable resolution! Using defaults {width}x{height}"
    logging.getLogger(__name__).info(msg)
    return default_width, default_height
