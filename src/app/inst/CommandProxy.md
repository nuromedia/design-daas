#!/usr/bin/python3

import os
import socket
import click
import subprocess
import logging
import json as json_parser


@click.group
def CommandProxyClick():
    """
    Spawns a new process with specified parameters
    """
    pass


@CommandProxyClick.command
@click.argument("args", nargs=-1)
def invoke(args: list):
    """
    Invokes api command with specified arguments
    """
    proxy = CommandProxy()
    return proxy.invoke(args)


class CommandProxy:
    def __init__(self):
        self.version = "0.0.1"
        self.__init_logging()

    def invoke(self, args: list):
        """
        Invokes api command with specified arguments
        """
        if args[0] == "cmd":
            return self.__execute_cmd(args[1:])
        elif args[0] == "action":
            return self.__execute_action(args[1], " ".join(args[2:]))
        else:
            logging.getLogger(__class__.__name__).info(
                f"Unknown API command: {args}"
            )
            return -1

    def __execute_action(self, action: str, args: str):
        """
        Executes specified action
        """
        if action == "status":
            msg = (
                f"\nOS        : {os.name}\n"
                f"Hostname  : {socket.gethostname()}\n"
                f"IP        : {socket.gethostbyname(socket.getfqdn())}"
            )
            logging.getLogger(__class__.__name__).info(msg)
        elif action == "version":
            msg = f"VERSION: {self.version}"
            logging.getLogger(__class__.__name__).info(msg)
        elif action == "ping":
            msg = f"ACTION: ping {args} -> pong {args}"
            logging.getLogger(__class__.__name__).info(msg)
        elif action == "install":
            msg = f"ACTION: install {args}"
            logging.getLogger(__class__.__name__).info(msg)
            return self.__execute_installer(args)
        elif action == "uninstall":
            msg = f"ACTION: uninstall {args}"
            logging.getLogger(__class__.__name__).info(msg)
            return self.__execute_uninstaller(args)
        else:
            msg = f"Unknown API action: {action} {args}"
            logging.getLogger(__class__.__name__).error(msg)
            raise ValueError(msg)
        return msg

    def __execute_installer(self, args: str):
        js = json_parser.loads(args)
        if js != None:
            if "type" in js and "name" in js:
                type = js["type"]
                name = js["name"]
                msg = f"Installing '{type}' with name '{name}'"
                logging.getLogger(__class__.__name__).info(msg)
                if type == "apt" and os.name == "posix":
                    return self.__try_spawn_process(
                        ["sudo", "apt", "install", "-y", name]
                    )
                elif type == "winget" and os.name == "nt":
                    return self.__try_spawn_process(
                        [
                            "powershell.exe",
                            "winget",
                            "install",
                            name,
                            "--disable-interactivity",
                            "--accept-source-agreements",
                        ]
                    )

    def __execute_uninstaller(self, args: str):
        js = json_parser.loads(args)
        if js != None:
            if "type" in js and "name" in js:
                type = js["type"]
                name = js["name"]
                msg = f"Uninstalling '{type}' with name '{name}'"
                logging.getLogger(__class__.__name__).info(msg)
                if type == "apt" and os.name == "posix":
                    return self.__try_spawn_process(
                        ["sudo", "apt", "remove", "-y", name]
                    )
                elif type == "winget" and os.name == "nt":
                    return self.__try_spawn_process(
                        [
                            "powershell.exe",
                            "winget",
                            "uninstall",
                            name,
                            "--disable-interactivity",
                            "--accept-source-agreements",
                        ]
                    )

    def __execute_cmd(self, args: str):
        """
        Executes specified command line
        """
        return self.__try_spawn_process(args)

    def __try_spawn_process(self, cmd: str):
        """
        Spawns the specified process
        """
        theproc = None
        txtOut = ""
        txtErr = ""
        try:
            if os.name == "nt":
                print("FOO")
                cmdstr = " ".join(cmd)
                cmd = f"C:/Users/user/daas/env/pstools/psexec.exe -nobanner -accepteula -i 1 -u user -p user {cmdstr}"
                # cmd = f"psexec -nobanner -accepteula -i 1 -u user -p user {cmdstr}"
                theproc = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                # theproc.wait()
                txtOut = theproc.stdout  # .read().decode()
                txtErr = theproc.stderr  # .read().decode()
                print(f"{txtOut}{txtErr}")
                return [theproc.returncode, txtOut, txtErr]
            elif os.name == "posix":
                # cmdstr = " ".join(cmd)
                # cmd = f"{cmdstr}"
                # cmd = "apt install psmisc".encode()
                # cmd = ["sudo", "apt", "install", "psmisc"]
                # print("FinalCMD: " + str(cmd))
                theproc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                theproc.wait()
                txtOut = theproc.stdout.read().decode()
                txtErr = theproc.stderr.read().decode()
                print(f"{txtOut}{txtErr}")
                return [theproc.returncode, txtOut, txtErr]
        except Exception as e:
            logging.getLogger(__class__.__name__).error(
                "Unknown error on process spawn!"
            )
            logging.getLogger(__class__.__name__).error(
                f"Command was: {cmd} -> {e}"
            )
            raise OSError("Unknown error on process spawn!")

    def __init_logging(self):
        logging.basicConfig(
            format="%(asctime)s [%(levelname)-5.5s] %(name)-20s: %(message)s",
            datefmt="%m/%d/%y %H:%M:%S",
            encoding="utf-8",
            level=logging.DEBUG,
            handlers=[
                # logging.FileHandler("example.log"),
                logging.StreamHandler()
            ],
        )


if __name__ == "__main__":
    CommandProxyClick()
