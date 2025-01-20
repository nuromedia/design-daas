import os
import subprocess
from dataclasses import dataclass

from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class SshAdapterConfig:
    """Config for SshAdapter"""

    sshuser: str
    sshhost: str
    sshport: int
    sshopt_timeout: int
    sshopt_strictcheck: str
    sshopt_nohostauth: str
    logcmd: bool
    logresult: bool


class SshAdapter(Loggable):
    """Adapter to perform ssh requests"""

    def __init__(self, cfg: SshAdapterConfig):
        Loggable.__init__(self, LogTarget.SSH)
        self.config = cfg

    def __str__(self):
        return f"{self.config}"

    def scp_upload_call(self, src: str, dst: str) -> tuple[int, str, str]:
        """
        Copies files via scp and given arguments
        """
        remote_folder = os.path.dirname(dst)
        folder_cmd = f"mkdir -p {remote_folder}"
        folder_created, folder_out, folder_err = self.ssh_call(folder_cmd)
        if folder_created != 0:
            return folder_created, folder_out, folder_err

        args = f"{src} {self.config.sshuser}@{self.config.sshhost}:{dst}"
        full_command = [
            "scp",
            "-o",
            f"ConnectTimeout={self.config.sshopt_timeout}",
            "-o",
            f"StrictHostKeyChecking={self.config.sshopt_strictcheck}",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            f"NoHostAuthenticationForLocalhost={self.config.sshopt_nohostauth}",
            "-o",
            "LogLevel=quiet",
            "-P",
            f"{self.config.sshport}",
            src,
            f"{self.config.sshuser}@{self.config.sshhost}:{dst}",
        ]
        try:
            process = subprocess.run(
                full_command, capture_output=True, text=True, check=True
            )
            std_out = ""
            std_err = ""
            if process.stdout is not None:
                std_out = str(process.stdout)
            if process.stderr is not None:
                std_err = str(process.stderr)
            self._print_result(args, process.returncode, std_out, std_err)
            return (process.returncode, std_out, std_err)
        except Exception as ex:
            self._log_error(f"{str(ex)} -> {args}", 1)
            raise OSError("Ssh execution failed for unknown reason!") from ex

    def ssh_call(self, args: str) -> tuple[int, str, str]:
        """
        Spawns a process with given arguments
        """
        full_command = [
            "ssh",
            "-o",
            f"ConnectTimeout={self.config.sshopt_timeout}",
            "-o",
            f"StrictHostKeyChecking={self.config.sshopt_strictcheck}",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            f"NoHostAuthenticationForLocalhost={self.config.sshopt_nohostauth}",
            "-o",
            "LogLevel=quiet",
            "-p",
            f"{self.config.sshport}",
            f"{self.config.sshuser}@{self.config.sshhost}",
            args,
            "&",
        ]
        # self.__log_info(f"SSHARGS: {full_command}")
        # pylint: disable=broad-exception-caught
        try:
            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=True,
                shell=False,
                encoding="cp850",
            )

            std_out = ""
            std_err = ""
            if process.stdout is not None:
                std_out = str(process.stdout)
            if process.stderr is not None:
                std_err = str(process.stderr)
            if std_out.endswith("\n"):
                std_out = std_out[:-1]
            if std_err.endswith("\n"):
                std_err = std_err[:-1]
            self._print_result(args, process.returncode, std_out, std_err)
            return (process.returncode, std_out, std_err)
        except UnicodeDecodeError as exe:
            self._log_error(f"UnicodeDecodeError Exception raised: {exe}", -1)
            return -1, "", f"UnicodeDecodeError Exception raised: {exe}"

        except Exception as exe:
            hdr = "SSHERR"
            msg = f"{hdr:>6} {str(exe)} -> {args} {type(exe)}"
            self._log_error(msg, -1)
            return -1, "", f"Exception raised: {exe}"

    def _print_result(self, args, code, str_out, str_err):
        msg = ""
        if self.config.logcmd:
            msg = f"{args}"
        if self.config.logresult:
            if msg != "":
                msg += " "
            if str_out != "":
                msg += f"{msg}{str_out}"
            if str_err != "":
                msg += f"{msg}{str_err}"
        if msg != "":
            self._log_info(msg, code)
