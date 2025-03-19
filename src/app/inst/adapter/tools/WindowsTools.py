"""
Windows helpers
"""

import time
import os
import subprocess
from dataclasses import dataclass
from typing import List
import psutil
import pywintypes

import win32gui
import win32process
import win32con
import win32api


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


def process_run(prog: str, args: list, shell: bool, codepage: str) -> tuple:
    """
    Runs a command within Windows
    """
    # Prepare execution
    result = -1
    txt_out = ""
    txt_err = ""
    all_args = [prog]
    all_args.extend(args)
    # Run command
    try:
        theproc = subprocess.run(
            all_args,
            text=True,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding=codepage,
            check=False,
        )
        # Extract printed text
        if theproc is not None:
            if theproc.returncode != 0:
                result = 0
            if theproc.stdout is not None and theproc.stderr is not None:
                txt_out = theproc.stdout
                txt_err = theproc.stderr
        return result, txt_out, txt_err
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
        print(f"EXCEPTION in subprocess.run: {err}")
    return 1, "", "Unknown error in subprocess.run"


def process_popen(prog: str, args: list, shell: bool, codepage: str) -> int:
    """
    popens a command within Windows
    """

    result = -1
    all_args = [prog]
    all_args.extend(args)
    try:
        theproc = subprocess.Popen(
            all_args,
            text=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=shell,
            encoding=codepage,
        )
        if theproc is not None and theproc.returncode is not None:
            print("RUNNING")
            result = theproc.returncode
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
        print(f"Execption in subprocess.Popen: {err}")
    return result


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
        if proc_element is not None:
            if name != "":
                if name == proc_element.name:
                    result.append(proc_element)
            else:
                result.append(proc_element)
    return result


def process_kill(killterm: int | str, codepage: str):
    """
    Kill process by given pid
    """
    try:
        kill_args = []
        if isinstance(killterm, int):
            kill_args = ["/F", "/PID", f"{killterm}"]
        if isinstance(killterm, str):
            kill_args = ["/F", "/IM", f"{killterm}"]

        process_run("taskkill", kill_args, True, codepage)
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


def try_find_pid(searchterms: list, timeout: int) -> int:
    """
    Searches for a given list of searchterms in process list.
    Returns -1 if not found or the pid from the first matching process.
    """
    result = -1

    while timeout > 0:
        result = __find_pid(searchterms)
        if result != -1:
            break
        timeout -= 1
    return result


def get_windows_by_pid(pid: int) -> list:
    """
    Searches all windows belonging to a pid and for a given title
    """

    def callback(hwnd: int, hwnds: list):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            hwnds.append(hwnd)
        return True

    hwnds: List[int] = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def maximize_windows_by_pid(pid: int, searchterms: list):
    """
    Maximize the windows of a process
    """
    windows = []
    try:
        windows = get_windows_by_pid(pid)
        for hwnd in windows:
            text = win32gui.GetWindowText(hwnd)
            if text in searchterms:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                break
    except pywintypes.error as ex:
        print(f"Exception during window search: {ex}")


def get_resolution_list() -> list:
    """
    Enumerates available screen resolutions
    """
    reslist = []
    i = 0
    while True:
        try:
            setting = win32api.EnumDisplaySettings(None, i)
        except pywintypes.error:
            break
        reslist.append((setting.PelsWidth, setting.PelsHeight))
        i = i + 1
    return list(reversed(sorted(reslist)))


def get_resolution_by_dimension(width: int, height: int) -> tuple:
    """
    Returns screen resolution which is smaller or equal the given size
    """
    result = 0, 0
    reslist = get_resolution_list()
    for resolution in reslist:
        if resolution[0] <= width and resolution[1] <= height:
            result = resolution[0], resolution[1]
            break
    return result


def tightvnc_update(pid: int, filename: str, codepage: str):
    """
    Configures tightvnc to only share a single app window
    """
    __tightvnc_app_stop(codepage, filename)
    __tightvnc_app_start(codepage, filename)
    __tightvnc_app_share(pid, codepage, filename)


def persist_pid(pid: int, username: str):
    """
    Persists pid to local disk
    """
    pidpath = __get_pid_path(username)
    try:
        statuspath = __get_status_path(username)
        os.mkdir(statuspath)
        with open(f"{pidpath}", "+w", encoding="utf-8") as handle:
            handle.write(str(pid))
    except FileExistsError:
        pass
    except OSError:
        pass


def clean_session(codepage: str) -> int:
    """
    PSTools leaves sessions open after executing commands
    Dirty workaround: Clean them up, no matter what
    """
    return process_popen("net", ["session", "/DELETE", "/Y"], True, codepage)


def normalize_prog_name(prog: str) -> str:
    """
    Normalizes the command from given args.
    Takes care of slashes and quotes at the start or end of the string
    """
    prog = prog.replace("/", "\\")
    if prog.startswith("'") or prog.startswith('"'):
        prog = prog[1:]
    if prog.endswith("'") or prog.endswith('"'):
        prog = prog[:-1]
    return prog


def generate_searchterms(searchname: str, mapping_uwp: dict) -> list[str]:
    """
    Produces a list of plausible searchterms for a given program
    """
    result = []
    filename_ext = os.path.basename(searchname)
    filename_raw, _ = os.path.splitext(filename_ext)

    normname = normalize_prog_name(searchname)
    normfile_ext = normalize_prog_name(filename_ext)
    normfile_raw = normalize_prog_name(filename_raw)
    result.append(searchname.upper())
    result.append(normname.upper())
    result.append(normfile_ext.upper())
    result.append(normfile_raw)
    for uwpcheck in (
        searchname,
        filename_ext,
        filename_raw,
        normname,
        normfile_ext,
        normfile_raw,
    ):
        if uwpcheck.upper() in mapping_uwp:
            result.append(mapping_uwp[uwpcheck.upper()])
    return result


def construct_ospackage_arguments(install: bool, name: str) -> list[str]:
    """
    Construct winget arguments for install and uninstall calls
    """
    args = []
    if install:
        args = [
            "install",
            name,
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]
    else:
        args = [
            "uninstall",
            name,
            "--accept-source-agreements",
        ]
    return args


def set_current_resolution(width: int, height: int):
    """
    Sets the currently used screen resolution
    """
    devmode = pywintypes.DEVMODEType()
    devmode.PelsWidth = width
    devmode.PelsHeight = height
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
    win32api.ChangeDisplaySettings(devmode, 0)


def get_current_resolution(args: list) -> tuple:
    """
    Retrieves currently used screen resolution
    """
    hmonitor = win32api.MonitorFromPoint((0, 0))
    monitor_info = win32api.GetMonitorInfo(hmonitor)
    monitor_area = monitor_info["Monitor"]
    width = monitor_area[2] - monitor_area[0]
    height = monitor_area[3] - monitor_area[1]
    return width, height


def __find_pid(searchterms: list) -> int:
    result = -1

    proglist = get_process_list()
    for single in proglist:
        cmptext = single.name.upper()
        if cmptext in searchterms:
            result = single.pid
            break
    return result


def __tightvnc_app_share(pid: int, codepage: str, filename: str):
    print("Sharing APP via TIGHTVNC")
    process_popen(
        filename,
        ["-controlapp", "-shareapp", str(pid)],
        False,
        codepage,
    )


def __tightvnc_app_start(codepage: str, filename: str):
    print("Starting TIGHTVNC")
    process_popen(filename, ["-run"], False, codepage)
    time.sleep(1)


def __tightvnc_app_stop(codepage: str, filename: str):
    print("Stopping TIGHTVNC")
    process_popen(filename, ["-stop", "-silent"], False, codepage)
    process_popen(filename, ["-controlapp", "-disconnectall"], False, codepage)
    process_kill("tvnserver.exe", codepage)


def __get_pid_path(username: str):
    return f"{__get_status_path(username)}/pid.txt"


def __get_status_path(username: str):
    return f"C:/Users/{username}/daas/status"
