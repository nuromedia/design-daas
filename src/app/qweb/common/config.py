"""Qweb config"""

import os
from dataclasses import dataclass
import tomllib
from typing import Any

DEFAULT_PORT = 5000
DEFAULT_HOST = "0.0.0.0"
DEFAULT_EXT_PORT = 443
DEFAULT_EXT_HOST = "cluster.daas-design.de"
DEFAULT_EXT_PROTO = "https"
DEFAULT_DEBUG = True
DEFAULT_TESTING = True
DEFAULT_TIMINGS = True
DEFAULT_ARGS = True
DEFAULT_EXCEPTIONS = True
DEFAULT_RECURSIONS = 3000
DEFAULT_DATA_PATH = "data"
DEFAULT_CERTFILE = "data/keys/cert.pem"
DEFAULT_KEYFILE = "data/keys/key.pem"

DEFAULT_LAUTH_ID = 5
DEFAULT_LAUTH_NAME = "default_user"
DEFAULT_RAUTH_URL = "http://auth.yourdomain"
DEFAULT_RAUTH_CLIENTID = ""
DEFAULT_RAUTH_SCOPE = ""
DEFAULT_RAUTH_USERNAME = ""
DEFAULT_RAUTH_PASSWORD = ""


@dataclass
class BlueprintHandlerConfig:
    """Quart service config parameters"""

    enable_debugging: bool
    enable_testing: bool
    enable_timings: bool
    enable_exceptions_echo: bool
    enable_args_echo: bool
    recursion_limit: int


@dataclass
class QwebSysConfig:
    """Qweb system parameters"""

    root_path: str
    data_path: str


@dataclass
class QuartConfig:
    """Quart config parameters"""

    root_path: str
    config_folder: str
    webroot_folder: str
    static_folder: str
    template_folder: str


@dataclass
class QuartRunConfig:
    """Quart run config parameters"""

    port: int
    host: str
    debug: bool


@dataclass
class QuartProcessorConfig:
    """Quart processor config parameters"""

    hostproto: str
    hostip: str
    hostport: int


@dataclass
class CorsConfig:
    """Cors config parameters"""

    enabled: bool
    allow_origin: list[str]
    allow_headers: list[str]
    allow_methods: list[str]
    allow_credentials: bool


@dataclass
class SslConfig:
    """Ssl config parameters"""

    enabled: bool
    certfile: str
    keyfile: str


@dataclass
class QwebConfig:
    """Qweb config parameters"""

    sys: QwebSysConfig
    quart: QuartConfig
    handler: BlueprintHandlerConfig
    run: QuartRunConfig
    cors: CorsConfig
    proc: QuartProcessorConfig
    ssl: SslConfig


@dataclass
class QwebLocalAuthenticatorConfig:
    """Qweb local auth config parameters"""

    default_userid: int
    default_username: str


@dataclass
class QwebRemoteAuthenticatorConfig:
    """Qweb remote auth config parameters"""

    url: str
    clientid: str
    scope: str
    username: str
    password: str


@dataclass
class QwebAuthenticatorConfig:
    """Qweb auth config parameters"""

    authenticator_type: str
    enable_auth_user: bool
    enable_auth_token: bool
    enable_auth_endpoint: bool
    enable_entity_verification: bool
    enable_verify_tls: bool
    enable_logging: bool
    enable_log_entity_verification: bool
    enable_log_requests: bool
    enable_log_results: bool
    local: QwebLocalAuthenticatorConfig
    remote: QwebRemoteAuthenticatorConfig


class ConfigReader:
    """Provides config"""

    cfg_qweb: QwebConfig
    cfg_auth: QwebAuthenticatorConfig

    def __init__(self, qwebfile: str = "", authfile: str = ""):
        if qwebfile != "":
            self.cfg_qweb = self.create_qweb_config_toml(qwebfile)
        else:
            self.cfg_qweb = self.create_qweb_config_defaults()
        if authfile != "":
            self.cfg_auth = self.create_auth_config_toml(authfile)
        else:
            self.cfg_auth = self.create_auth_config_defaults()

    def create_qweb_config_toml(self, file: str):
        """Creates qweb config from file"""
        conf = self._read_toml(file)
        sys = QwebSysConfig(**conf["sys"], root_path=os.getcwd())
        ssl = SslConfig(**conf["ssl"])
        if ssl.keyfile.startswith("/") is False:
            ssl.keyfile = f"{sys.data_path}/{ssl.keyfile}"
        if ssl.certfile.startswith("/") is False:
            ssl.certfile = f"{sys.data_path}/{ssl.certfile}"
        return QwebConfig(
            sys=sys,
            cors=CorsConfig(**conf["cors"]),
            handler=BlueprintHandlerConfig(**conf["handler"]),
            run=QuartRunConfig(**conf["run"]),
            quart=QuartConfig(**conf["quart"], root_path=sys.root_path),
            proc=QuartProcessorConfig(**conf["template_args"]),
            ssl=ssl,
        )

    def create_auth_config_toml(self, file: str):
        """Creates auth config from file"""
        conf = self._read_toml(file)
        return QwebAuthenticatorConfig(**conf["auth"])

    def create_qweb_config_defaults(self):
        """Provides default config"""
        return QwebConfig(
            cors=CorsConfig(
                enabled=True,
                allow_origin=["*"],
                allow_headers=["*"],
                allow_methods=["*"],
                allow_credentials=False,
            ),
            sys=QwebSysConfig(
                root_path=os.getcwd(),
                data_path=DEFAULT_DATA_PATH,
            ),
            handler=BlueprintHandlerConfig(
                enable_debugging=DEFAULT_DEBUG,
                enable_testing=DEFAULT_TESTING,
                enable_timings=DEFAULT_TIMINGS,
                enable_args_echo=DEFAULT_ARGS,
                enable_exceptions_echo=DEFAULT_EXCEPTIONS,
                recursion_limit=DEFAULT_RECURSIONS,
            ),
            run=QuartRunConfig(
                debug=DEFAULT_DEBUG,
                host=DEFAULT_HOST,
                port=DEFAULT_PORT,
            ),
            proc=QuartProcessorConfig(
                hostproto=DEFAULT_EXT_PROTO,
                hostip=DEFAULT_EXT_HOST,
                hostport=DEFAULT_EXT_PORT,
            ),
            quart=QuartConfig(
                root_path=os.getcwd(),
                config_folder="config",
                webroot_folder=f"{DEFAULT_DATA_PATH}/webroot",
                template_folder=f"{DEFAULT_DATA_PATH}/webroot/templates",
                static_folder=f"{DEFAULT_DATA_PATH}/webroot/static",
            ),
            ssl=SslConfig(
                enabled=True,
                certfile=DEFAULT_CERTFILE,
                keyfile=DEFAULT_KEYFILE,
            ),
        )

    def create_auth_config_defaults(self):
        """Provides default auth config"""
        return QwebAuthenticatorConfig(
            authenticator_type="local",
            enable_auth_user=True,
            enable_auth_token=True,
            enable_auth_endpoint=True,
            enable_entity_verification=True,
            enable_verify_tls=False,
            enable_logging=True,
            enable_log_entity_verification=True,
            enable_log_requests=True,
            enable_log_results=True,
            local=QwebLocalAuthenticatorConfig(DEFAULT_LAUTH_ID, DEFAULT_LAUTH_NAME),
            remote=QwebRemoteAuthenticatorConfig(
                url=DEFAULT_RAUTH_URL,
                clientid=DEFAULT_RAUTH_CLIENTID,
                scope=DEFAULT_RAUTH_SCOPE,
                username=DEFAULT_RAUTH_USERNAME,
                password=DEFAULT_RAUTH_PASSWORD,
            ),
        )

    def _read_toml(self, file: str) -> dict[str, Any]:
        """Creates config from file"""
        if os.path.exists(file):
            with open(file=file, mode="rb") as pointer:
                return tomllib.load(pointer)
        return {}
