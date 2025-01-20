from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True)
class DatabaseConfig:
    """Config for databases"""

    database: str
    """
    File path to the database.

    Example: `daas.sqlite`

    The file will be created if it doesn't exist.

    If a transient DB is needed, specify a tempfile.
    The special SQlite `:memory:` name does technically work,
    but since the application creates multiple connections they'd 
    all have fresh database instances which doesn't work.
    """
    data_path: str
    db_name: str
    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_type: str

    enable_echo: bool = False

    admin_credentials: Optional[str] = None
    """
    `username:password` for an admin account.

    Example value: `"admin:s3cret!"`

    If this variable is set, the application will store 
    these credentials in the database for password authentication.
    This is great for test environments and for initial configuration.
    """

    include_samples: bool


@dataclass
# pylint: disable=too-many-instance-attributes
class InstanceControllerConfig:
    """
    Config object for InstanceController
    """

    sshuser: str
    sshport: int
    sshopt_timeout: int
    sshopt_strictcheck: str
    sshopt_nohostauth: str
    prefixip: str
    proxyfile: str
    logcmd: bool
    logresult: bool
    enable_message_queue: bool
    test_method_online_state: str
