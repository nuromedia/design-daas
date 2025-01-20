"""Manages loggers"""

from enum import Enum
import os
import logging
import logging.config
from dataclasses import dataclass
import traceback
from typing import Optional


class LogTarget(Enum):
    DB = "db"
    NODE = "node"
    ANY = "any"
    SYS = "sys"
    QWEB = "qweb"
    LAYERS = "layers"
    RUNTIME = "runtime"
    PROC = "proc"
    PLUGIN = "plugin"
    AUTH = "auth"
    WEBSOCKET = "websocket"
    PROXY = "proxy"
    INST = "inst"
    TASK = "task"
    FILES_LOCAL = "file"
    FILES_CEPH = "ceph"
    CONTAINER = "container"
    FRONTEND = "frontend"
    BACKEND = "backend"
    OBJECT = "object"
    AUTOMATION = "auto"
    LIMIT = "limit"
    HTTP = "http"
    QMSG = "qmsg"
    SSH = "ssh"
    VM = "vm"


class Loggable:
    def __init__(self, target: LogTarget):
        self.log_target = target
        self.logger = logging.getLogger(self.log_target.value)

    def _log_info(self, msg: str, code: Optional[int | bool] = None) -> None:
        """Logs info message"""
        exitcode = -1
        if isinstance(code, bool):
            exitcode = 0 if code is True else 1
        elif isinstance(code, int):
            exitcode = code
        msg = self._prefix_code(msg, exitcode)
        if hasattr(self, "logger") is False:
            self.logger = logging.getLogger("default")
        if self.logger is not None:
            return self.logger.info(msg)
        print(f"No Logger! Using fallback: {msg}")

    def _log_debug(self, msg: str, code: Optional[int | bool] = None) -> None:
        """Logs debug message"""
        msg = self._prefix_code(msg, code)
        if self.logger is not None:
            return self.logger.debug(msg)
        print(f"No Logger! Using fallback: {msg}")

    def _log_warn(self, msg: str, code: Optional[int | bool] = None) -> None:
        """Logs warning message"""
        msg = self._prefix_code(msg, code)
        if self.logger is not None:
            return self.logger.warning(msg)
        print(f"No Logger! Using fallback: {msg}")

    def _log_error(
        self,
        msg: str,
        code: Optional[int | bool] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """Logs error message"""
        from app.qweb.service.service_runtime import get_qweb_runtime

        msg = self._prefix_code(msg, code)
        runtime = get_qweb_runtime()
        error_msg = ""
        error_trace = ""
        if exception is not None:
            error_msg = f" {type(exception).__qualname__}! {exception}"
            if runtime.cfg_qweb.handler.enable_debugging:
                error_trace = f"\n{traceback.format_exc()}"
        if self.logger is not None:
            return self.logger.error(f"{msg}{error_msg}{error_trace}")
        print(f"No Logger! Using fallback: {msg}{error_msg}{error_trace}")

    def _prefix_code(self, msg: str, code: Optional[int | bool] = None) -> str:
        code = self._convert_code(code)
        if code != -1:
            return f"{code:3} -> {msg}"
        return msg

    def _convert_code(self, code: Optional[int | bool] = None) -> int:
        exitcode = -1
        if isinstance(code, bool):
            exitcode = 0 if code is True else 1
        elif isinstance(code, int):
            exitcode = code
        return exitcode


@dataclass(kw_only=True)
class LoggerConfig:
    """Config for logging"""

    enabled: bool = True
    console_target: str = "console"
    debug_target: str = "debug"
    error_target: str = "error"
    all_sublogs: bool = False
    no_sublogs: bool = False
    log_hypercorn: bool = False
    log_web_enabled: bool = False
    log_web_resize: bool = False
    log_web_tunnel: bool = False
    log_web_client: bool = False
    log_web_watcher: bool = False
    log_web_switcher: bool = False
    log_web_summary: bool = False
    log_any: bool = False
    log_db: bool = False
    log_sys: bool = False
    log_node: bool = False
    log_qweb: bool = False
    log_runtime: bool = False
    log_proc: bool = False
    log_layers: bool = False
    log_plugin: bool = False
    log_auth: bool = False
    log_proxy: bool = False
    log_websocket: bool = False
    log_inst: bool = False
    log_tasks: bool = False
    log_files_local: bool = False
    log_files_ceph: bool = False
    log_frontend: bool = False
    log_objects: bool = False
    log_limits: bool = False
    log_backend: bool = False
    log_container: bool = False
    log_automation: bool = False
    log_vm: bool = False
    log_adapter_qmsg: bool = False
    log_adapter_ssh: bool = False
    log_adapter_http: bool = False
    log_error: bool = False
    log_debug: bool = False
    log_console: bool = False
    log_console_exclude: list
    log_dir: str = "logs"
    log_level: str = "DEBUG"
    log_prefix: str = "[%(asctime)s][API][%(levelname)-5.5s]:"
    log_message: str = "%(message)s"
    log_details: str = "[%(name)s:%(lineno)d]"
    log_date: str = "%Y-%m-%d %H:%M:%S"
    log_encode: str = "utf-8"


class QwebLogManager:
    """Manages loggers"""

    def __init__(self, cfg: LoggerConfig):
        self.cfg = cfg
        self.console_target = self.cfg.console_target
        self.debug_target = self.cfg.debug_target
        self.error_target = self.cfg.error_target
        self.default_formatter = "defaultFormatter"
        self.version: int = 1
        self.formatters: dict = {}
        self.handlers: dict = {}
        self.loggers: dict = {}
        self.root_loggers: dict = {}
        self.all_loggers: dict = {}
        self.dict_conf: dict = {}

    def __repr__(self) -> str:
        result = (
            f"{self.__class__.__qualname__}("
            f"loggers={len(self.loggers)},"
            f"handlers={len(self.handlers)},"
            f"formatters={len(self.formatters)}"
            ")"
        )
        return result

    def initialize_logging(self) -> bool:
        """Initialize logging"""
        self._ensure_folders()
        self._configure_hypercorn()
        self._create_logger_config(
            self._create_formatter_list(), self._create_target_list()
        )
        ret = self._apply_config()
        self.logger = logging.getLogger(LogTarget.SYS.value)
        self._log_info("Initialized logging")
        return ret

    def _create_formatter_list(self) -> list[str]:
        result = [self.default_formatter]
        return result

    def _create_target_list(self) -> list[str]:
        result = []
        if self.cfg.log_any:
            result.append(LogTarget.ANY.value)
        if self.cfg.log_node:
            result.append(LogTarget.NODE.value)
        if self.cfg.log_db:
            result.append(LogTarget.DB.value)
        if self.cfg.log_qweb:
            result.append(LogTarget.QWEB.value)
        if self.cfg.log_runtime:
            result.append(LogTarget.RUNTIME.value)
        if self.cfg.log_proc:
            result.append(LogTarget.PROC.value)
        if self.cfg.log_layers:
            result.append(LogTarget.LAYERS.value)
        if self.cfg.log_sys:
            result.append(LogTarget.SYS.value)
        if self.cfg.log_plugin:
            result.append(LogTarget.PLUGIN.value)
        if self.cfg.log_auth:
            result.append(LogTarget.AUTH.value)
        if self.cfg.log_proxy:
            result.append(LogTarget.PROXY.value)
        if self.cfg.log_websocket:
            result.append(LogTarget.WEBSOCKET.value)
        if self.cfg.log_inst:
            result.append(LogTarget.INST.value)
        if self.cfg.log_tasks:
            result.append(LogTarget.TASK.value)
        if self.cfg.log_files_local:
            result.append(LogTarget.FILES_LOCAL.value)
        if self.cfg.log_files_ceph:
            result.append(LogTarget.FILES_CEPH.value)
        if self.cfg.log_frontend:
            result.append(LogTarget.FRONTEND.value)
        if self.cfg.log_backend:
            result.append(LogTarget.BACKEND.value)
        if self.cfg.log_container:
            result.append(LogTarget.CONTAINER.value)
        if self.cfg.log_vm:
            result.append(LogTarget.VM.value)
        if self.cfg.log_automation:
            result.append(LogTarget.AUTOMATION.value)
        if self.cfg.log_objects:
            result.append(LogTarget.OBJECT.value)
        if self.cfg.log_limits:
            result.append(LogTarget.LIMIT.value)
        if self.cfg.log_adapter_qmsg:
            result.append(LogTarget.QMSG.value)
        if self.cfg.log_adapter_http:
            result.append(LogTarget.HTTP.value)
        if self.cfg.log_adapter_ssh:
            result.append(LogTarget.SSH.value)
        return result

    def _ensure_folders(self):
        if os.path.exists(self.cfg.log_dir) is False:
            os.makedirs(self.cfg.log_dir)

    def _configure_hypercorn(self):
        if self.cfg.log_hypercorn is False:
            logging.getLogger("hypercorn.access").disabled = False

    def _create_logger_config(
        self,
        formatters: list[str],
        targets: list[str],
    ) -> dict:
        result = {}
        stream_targets = [self.console_target]
        file_targets = [self.debug_target, self.error_target]
        file_targets.extend(targets)
        self.formatters = self._initialize_formatters(formatters)
        self.handlers = self._initialize_handlers(
            self.default_formatter, stream_targets, file_targets
        )
        self.loggers = self._initialize_loggers(targets)
        result["version"] = self.version
        result["formatters"] = self.formatters
        result["handlers"] = self.handlers
        result["loggers"] = self.loggers
        self.root_loggers = self._configure_root_handlers(result, targets)
        self.all_loggers = self._configure_log_handlers(result, targets)
        self.dict_conf = result
        return self.dict_conf

    def _apply_config(self) -> bool:
        logging.config.dictConfig(self.dict_conf)
        self.logger = logging.getLogger(self.console_target)
        return True

    def _log_info(self, msg: str):
        self.logger.info(msg)

    def _initialize_handlers(
        self, formatter: str, stream_targets: list[str], file_targets: list[str]
    ) -> dict:
        handlers = {}
        for handler in stream_targets:
            name, conf = self._create_handler(handler, formatter, False)
            handlers[name] = conf
        for handler in file_targets:
            name, conf = self._create_handler(handler, formatter, True)
            handlers[name] = conf
        return handlers

    def _initialize_formatters(self, formatter_names: list[str]):
        log_format = self._create_logformat()
        formatter = self._create_formatter(log_format)
        formatters = {}
        for name in formatter_names:
            formatters[name] = formatter
        return formatters

    def _initialize_loggers(self, config_targets: list[str]) -> dict:
        rootname, rootlog = self._create_logger("")
        loggers = {rootname: rootlog}

        for target in config_targets:
            name, conf = self._create_logger(target)
            loggers[name] = conf
        return loggers

    def _configure_root_handlers(self, result: dict, config_targets: list[str]) -> dict:
        root_handlers = result["loggers"][""]["handlers"]
        if self.cfg.log_debug:
            root_handlers.append(f"{self.debug_target}.file")
        if self.cfg.log_error:
            root_handlers.append(f"{self.error_target}.file")
        if self.cfg.log_console:
            root_handlers.append(self.console_target)
            for target in config_targets:
                if target not in self.cfg.log_console_exclude:
                    target_handlers = result["loggers"][target]["handlers"]
                    target_handlers.append(self.console_target)
                    result["loggers"][target]["handlers"] = target_handlers
        result["loggers"][""]["handlers"] = root_handlers
        return root_handlers

    def _configure_log_handlers(self, result: dict, config_targets: list[str]) -> dict:
        for target in config_targets:
            target_handlers = result["loggers"][target]["handlers"]
            target_handlers.append(f"{target}.file")
            if self.cfg.log_debug:
                target_handlers.append(f"{self.debug_target}.file")
            if self.cfg.log_error:
                target_handlers.append(f"{self.error_target}.file")
            result["loggers"][target]["handlers"] = target_handlers
        return result["loggers"]

    def _create_handler(self, name: str, formatter: str, is_file: bool):
        outname = name
        handler_cls = "logging.StreamHandler"
        level = self.cfg.log_level
        if name == self.error_target:
            level = "ERROR"
        elif name == self.debug_target:
            level = "DEBUG"
        if is_file:
            handler_cls = "logging.FileHandler"
            outname = f"{name}.file"
        obj = {
            "level": level,
            "class": handler_cls,
            "formatter": formatter,
        }
        if is_file:
            obj["filename"] = f"{self.cfg.log_dir}/{name}.log"
        return outname, obj

    def _create_logger(self, name: str):
        outname = name
        propagate = False
        if name == "":
            propagate = True
        obj = {
            "handlers": [],
            "level": self.cfg.log_level,
            "propagate": propagate,
        }
        return outname, obj

    def _create_formatter(self, log_format: str):
        return {
            "format": log_format,
            "datefmt": self.cfg.log_date,
            "encoding": self.cfg.log_encode,
        }

    def _create_logformat(self):
        return f"{self.cfg.log_prefix} {self.cfg.log_message} {self.cfg.log_details}"
