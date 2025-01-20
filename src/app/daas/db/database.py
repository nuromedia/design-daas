"""
Provide state management via the ``Database`` class.
"""

from __future__ import annotations
import logging
import aiosqlite
from app.daas.common.config import DatabaseConfig
from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.common.model import Application
from app.daas.db.db_samples import SampleRegistry, SampleRegistryConfig
from app.daas.objects.object_application import ApplicationObject
from app.qweb.logging.logging import LogTarget
from app.daas.db.db_repos import (
    ApplicationRepository,
    ConnectionRepository,
    EnvironmentRepository,
    FileRepository,
    InstanceRepository,
    LimitRepository,
    ObjectRepository,
)

DEFAULT_ADMIN_ID = 5


class Database(
    LimitRepository,
    FileRepository,
    ApplicationRepository,
    ConnectionRepository,
    EnvironmentRepository,
    ObjectRepository,
    InstanceRepository,
):
    """
    A wrapper for database operations.
    Uses SQLAlchemy (ORM) for storing state.
    """

    def __init__(self) -> None:
        super().__init__()
        self.auth = AuthDatabase()

    async def connect(
        self,
    ) -> Database:
        """Connects database"""
        self.connected = await self._connect()
        return self

    async def disconnect(self) -> None:
        """Disconnects database"""
        await self._disconnect()

    async def load_demo_apps(self) -> None:
        """
        Prime the database with some apps
        that are known to be available for a demo.
        """
        from app.daas.objects.object_container import ContainerObject
        from app.daas.objects.object_machine import MachineObject

        cfg = await self._get_config_samples()
        logger = logging.getLogger(LogTarget.DB.value)
        registry = SampleRegistry(cfg=cfg)

        # if cfg.persist_session:
        #     session["userid"] = registry.config.default_owner
        #     session["user"] = registry.config.default_owner_name

        limitlist = registry.create_demo_limits()
        for testlimit in limitlist:
            if not await self.get_limit(testlimit.id_owner):
                msg = f"Import limit       : ({testlimit.id_owner})"
                logger.info(msg)
                await self.create_limit(testlimit)

        filelist = registry.create_demo_files()
        for testfile in filelist:
            if not await self.get_file(testfile.id):
                msg = f"Import file       : {testfile.name} ({testfile.id})"
                logger.info(msg)
                await self.create_file(testfile)

        objlist = registry.create_demo_objects()
        for obj in objlist:
            if not await self.get_daas_object(obj.id):
                msg = f"Import DB samples : {obj.id_user} ({obj.id})"
                if isinstance(obj, ContainerObject):
                    logger.info(msg)
                    await self.create_daas_object(obj)
                if isinstance(obj, MachineObject):
                    logger.info(msg)
                    await self.create_daas_object(obj)

        envs = registry.create_demo_environments()
        for env in envs:
            obj = await self.get_environment(env.id)
            if obj is None:
                await self.create_environment(env)

        cons = registry.create_demo_connection()
        for con in cons:
            obj = await self.get_guacamole_connection(con.id)
            if obj is None:
                await self.create_guacamole_connection(con)
        if len(objlist) > 0 and len(envs) > 0 and len(cons) > 0:
            insts = registry.create_demo_instances(objlist[0], envs[0], cons[0])
            for inst in insts:
                obj = await self.get_instance_by_id(inst.id)
                if obj is None:
                    await self.create_instance(inst)

        applist = registry.create_demo_applications()
        for testapp in applist:
            if isinstance(testapp, ApplicationObject):
                if not await self.get_application(testapp.id):
                    await self.create_application(testapp)

    async def _get_config_db(self) -> DatabaseConfig:
        dictconf = await self._get_config(ConfigFile.DB.value)
        return DatabaseConfig(**dictconf[ConfigSections.DB.value])

    async def _get_config_samples(self) -> SampleRegistryConfig:
        dictconf = await self._get_config(ConfigFile.DB.value)
        return SampleRegistryConfig(**dictconf[ConfigSections.SAMPLES.value])

    # async def connect_legacy(self, connstring: str):
    #     # pylint:disable=unnecessary-dunder-call
    #     if not os.path.exists(connstring):
    #         async with aiosqlite.connect(connstring, check_same_thread=False) as conn:
    #             self.conn = conn
    #             self.conn.row_factory = sqlite3.Row
    #             self.auth = AuthDatabase(self)
    #             await self.initialize_schema()
    #             self.__log_info(f"DB created        : {connstring}")
    #     if os.path.exists(connstring):
    #         self.conn = aiosqlite.connect(connstring, check_same_thread=False)
    #         await self.conn.__aenter__()
    #         self.conn.row_factory = sqlite3.Row
    #         self.connected = True
    #         self.__log_info(f"DB connected      : {connstring}")

    # async def disconnect_legacy(self) -> None:
    #     """
    #     Closes active database connections.
    #     """
    #     await self.conn.commit()
    #     await self.conn.close()
    #
    #     self.__log_info("Closed active db connection")

    # async def initialize_schema(self) -> None:
    #     """Initialize database schema, must be applied when the app starts."""
    #     (
    #         await self.conn.executescript(
    #             """
    #         PRAGMA foreign_keys = ON;
    #
    #         CREATE TABLE IF NOT EXISTS template_applications(
    #             id TEXT PRIMARY KEY,
    #             id_owner INT,
    #             id_file TEXT NULL,
    #             id_template TEXT NULL,
    #             os_type TEXT,
    #             name TEXT NOT NULL,
    #             installer TEXT,
    #             installer_args TEXT,
    #             installer_type TEXT,
    #             target TEXT,
    #             target_args TEXT,
    #             version TEXT,
    #             created_at TEXT
    #             ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS files (
    #             id TEXT PRIMARY KEY,
    #             id_owner INT,
    #             os_type TEXT,
    #             name TEXT NOT NULL,
    #             version TEXT,
    #             localpath TEXT,
    #             remotepath TEXT,
    #             filesize INT,
    #             created_at TEXT
    #             ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS limits (
    #             id_owner INT PRIMARY KEY,
    #             vm_max INT,
    #             container_max INT,
    #             obj_max INT,
    #             cpu_max INT,
    #             mem_max INT,
    #             dsk_max INT
    #             ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS instances (
    #             id TEXT PRIMARY KEY,
    #             id_con TEXT NULL REFERENCES guacamole_connections(id),
    #             id_app TEXT NOT NULL REFERENCES daas_objects(id),
    #             id_env TEXT,
    #             host TEXT NOT NULL,
    #             container TEXT NOT NULL,
    #             created_at TEXT NOT NULL,
    #             connected_at TEXT,
    #             booted_at TEXT
    #             ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS environments (
    #             id TEXT PRIMARY KEY,
    #             id_object TEXT NOT NULL REFERENCES daas_objects(id),
    #             id_backend TEXT NOT NULL,
    #             name TEXT NOT NULL,
    #             state TEXT NOT NULL,
    #             env_tasks TEXT,
    #             env_apps TEXT,
    #             env_target TEXT,
    #             created_at TEXT NOT NULL) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS guacamole_connections(
    #             id TEXT PRIMARY KEY REFERENCES instances(id_con) ON DELETE CASCADE,
    #             viewer_url TEXT NOT NULL,
    #             viewer_token TEXT NOT NULL,
    #             user TEXT NOT NULL,
    #             password TEXT NOT NULL,
    #             protocol TEXT NOT NULL,
    #             hostname TEXT NOT NULL,
    #             port INT NOT NULL) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS daas_objects (
    #             id TEXT PRIMARY KEY,
    #             id_user TEXT NOT NULL,
    #             id_owner INTEGER REFERENCES auth_password(id),
    #             id_proxmox INT,
    #             id_docker TEXT NOT NULL,
    #             object_type TEXT NOT NULL,
    #             object_mode TEXT NOT NULL,
    #             object_mode_extended TEXT NOT NULL,
    #             object_state TEXT NOT NULL,
    #             object_tasks TEXT,
    #             object_apps TEXT,
    #             object_target TEXT NOT NULL,
    #             object_storage TEXT,
    #             os_wine INTEGER NOT NULL,
    #             os_type TEXT NOT NULL,
    #             os_username TEXT NOT NULL,
    #             os_password TEXT NOT NULL,
    #             os_installer TEXT NOT NULL,
    #             hw_cpus INT,
    #             hw_memory INT,
    #             hw_disksize INT,
    #             ceph_public INTEGER,
    #             ceph_shared INTEGER,
    #             ceph_user INTEGER,
    #             vnc_port_system INT,
    #             vnc_port_instance INT,
    #             vnc_username TEXT,
    #             vnc_password TEXT,
    #             viewer_contype TEXT,
    #             viewer_resolution TEXT,
    #             viewer_resize TEXT,
    #             viewer_scale TEXT,
    #             viewer_dpi INTEGER,
    #             viewer_colors INTEGER,
    #             viewer_force_lossless INTEGER,
    #             extra_args TEXT NOT NULL
    #         ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS auth_password (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             username TEXT NOT NULL,
    #             password_hash TEXT NOT NULL
    #         ) STRICT;
    #
    #         CREATE TABLE IF NOT EXISTS auth_tokens (
    #            secret_token TEXT PRIMARY KEY,
    #            id TEXT NOT NULL UNIQUE,
    #            id_user INTEGER REFERENCES auth_password(id),
    #            description TEXT NOT NULL,
    #            created_at TEXT NOT NULL
    #         ) STRICT;
    #
    #         UPDATE sqlite_sequence SET seq = 5 WHERE name = 'auth_password';
    #         """
    #         )
    #     ).connection.commit()


async def _execute_sql_insert(
    conn: aiosqlite.Connection | aiosqlite.Cursor,
    *,
    table: str,
    values: dict,
    upsert_on: str | tuple[str, ...] = (),
) -> aiosqlite.Cursor:
    """
    Run a SQL 'insert' statement, with column names derived from the fields dict.

    Example:

    ```python
    await _execute_sql_insert(conn, table="foo", {"a": 1, "b": 2})
    ```

    is equivalent to:

    ```python
    await conn.execute('INSERT INTO foo(a, b) VALUES(:a, :b)', {"a": 1, "b": 2})
    ```

    This helps avoid typing out the column names three times.

    If the `upsert_on` argument is provided,
    an existing row is overwritten with the other fields:

    ```python
    await _execute_sql_insert(conn, table="foo", {"a": 1, "b": 2}, upsert_on="a")
    ```

    is equivalent to:

    ```python
    await conn.execute(
        '''
        INSERT INTO foo(a, b)
        VALUES(:a, :b)
        ON CONFLICT(a) DO UPDATE SET
          b = excluded.b
        ''',
        {"a": 1, "b": 2},
    )
    ```
    """
    columns = list(values)
    sql_columns = ", ".join(columns)
    sql_placeholders = ", ".join(f":{name}" for name in columns)
    sql = f"INSERT INTO {table}({sql_columns}) VALUES({sql_placeholders})"

    # potentially add upsert clause
    if isinstance(upsert_on, str):
        upsert_on = (upsert_on,)
    if upsert_on:
        conflict_cols = ", ".join(upsert_on)
        update_cols = ", ".join(
            f"{col} = excluded.{col}" for col in columns if col not in upsert_on
        )
        sql = f"{sql} ON CONFLICT({conflict_cols}) DO UPDATE SET {update_cols}"

    result = await conn.execute(sql, values)
    if isinstance(conn, aiosqlite.Connection):
        await conn.commit()
    return result


class AuthDatabase:
    """Auth-specific database operations."""

    def __init__(self) -> None:
        self.creds = {}

    async def save_password_hash(self, *, username: str, pwhash: str) -> None:
        """
        Save or update the password hash in the database.
        """

        values = {"id": -1, "password_hash": pwhash}
        if username == "admin":
            values["id"] = f"{DEFAULT_ADMIN_ID}"
        self.creds[username] = values

    async def get_password_hash(self, username: str) -> tuple[int, str]:
        """Retrieve a password hash for the given user."""
        if username in self.creds:
            return (
                self.creds[username]["id"],
                self.creds[username]["password_hash"],
            )
        return -1, ""

    # async def get_user_by_name(self, *, username: str) -> int:
    #     """Retrieves a user if available."""
    #     cursor = await self.conn.execute(
    #         "SELECT id, username FROM auth_password WHERE username = :username",
    #         {"username": username},
    #     )
    #     async with cursor:
    #         row = await cursor.fetchone()
    #         if not row:
    #             return -1
    #         (id_owner, _) = row
    #         result = id_owner
    #         cursor.connection.commit()
    #         return result

    # async def save_access_token(self, token: AccessToken, *, secret_token: str) -> None:
    #     """Save a new AccessToken."""
    #     (
    #         await _execute_sql_insert(
    #             self.conn,
    #             table="auth_tokens",
    #             values={
    #                 "secret_token": secret_token,
    #                 "id": token.id,
    #                 "id_user": token.id_user,
    #                 "description": token.description,
    #                 "created_at": _datetime_to_rfc3339(token.created_at),
    #             },
    #         )
    #     ).connection.commit()

    # async def delete_access_token(
    #     self,
    #     token_id: str,
    # ) -> None:
    #     """Delete an AccessToken by its ID."""
    #     (
    #         await self.conn.execute(
    #             "DELETE FROM auth_tokens WHERE id = :id", {"id": token_id}
    #         )
    #     ).connection.commit()

    # async def get_access_token_by_id(self, token_id: str) -> Optional[AccessToken]:
    #     """Retrieve metadata about an access token by its ID."""
    #     cursor = await self.conn.execute(
    #         """
    #         SELECT id, user, description, created_at
    #         FROM auth_tokens
    #         WHERE id = :id
    #         """,
    #         {"id": token_id},
    #     )
    #     async with cursor:
    #         row = await cursor.fetchone()
    #         if not row:
    #             return None
    #
    #         result = _make_access_token(row)
    #         cursor.connection.commit()
    #         return result
    #
    # async def get_access_token_by_secret(
    #     self, *, secret_token: str
    # ) -> Optional[AccessToken]:
    #     """
    #     Retrieve an AccessToken by its secret value.
    #     """
    #     cursor = await self.conn.execute(
    #         """
    #         SELECT id, id_user, description, created_at
    #         FROM auth_tokens
    #         WHERE secret_token = :secret_token
    #         """,
    #         {"secret_token": secret_token},
    #     )
    #     async with cursor:
    #         row = await cursor.fetchone()
    #         if not row:
    #             return None
    #
    #         result = _make_access_token(row)
    #         cursor.connection.commit()
    #         return result
    #
    # async def list_access_tokens(self, *, userid: int) -> list[AccessToken]:
    #     """Obtain all access tokens for the given userid."""
    #     cursor = await self.conn.execute(
    #         """
    #         SELECT id, id_user, description, created_at
    #         FROM auth_tokens
    #         WHERE id_user = :id_user
    #         """,
    #         {"id_user": userid},
    #     )
    #     async with cursor:
    #         result = [_make_access_token(row) for row in await cursor.fetchall()]
    #         cursor.connection.commit()
    #         return result
