"""Database manager"""

import os
from typing import Optional
from sqlalchemy.schema import MetaData
from sqlalchemy import Engine, create_engine
from app.daas.common.config import DatabaseConfig
from app.daas.db.db_api import DatabaseApi
from app.daas.db.db_model import ORMEntity
from app.qweb.logging.logging import LogTarget, Loggable


class DatabaseManager(Loggable):
    """Manages connections to the database"""

    def __init__(self, config: DatabaseConfig):
        Loggable.__init__(self, LogTarget.DB)
        self.cfg = config
        self.connected = False

    def initialize(self):
        self.engine = self.__create_engine()
        if self.engine is not None:
            self.metadata = ORMEntity.metadata
            self.metadata.create_all(self.engine)
            self.api = self._create_api(self.engine, self.metadata)
        else:
            raise ValueError("DB-Engine is None")

    def __create_engine(self) -> Optional[Engine]:
        if self.cfg.db_type == "mariadb":
            return self.__create_engine_mariadb()
        if self.cfg.db_type == "sqlite":
            return self.__create_engine_sqlite()
        return None

    def __create_engine_mariadb(self):
        self._log_info(
            f"Prepare engine: mariadb ({self.cfg.db_host}:{self.cfg.db_port})"
        )
        constring = self.__create_connection_string_mariadb(False)
        engine = create_engine(constring, echo=self.cfg.enable_echo)
        try:
            self.api = self._create_api(engine, ORMEntity.metadata)
            self.api.connect()
            self.api.db_session_create(self.cfg.db_name)
            self.api.disconnect()
            constring = self.__create_connection_string_mariadb()
            return create_engine(constring, echo=self.cfg.enable_echo)
        except Exception as exe:
            raise Exception(f"Error on db connect: {exe}")

    def __create_engine_sqlite(self):
        try:
            self._log_info(f"Prepare engine: sqlite ({self.cfg.db_name}.sqlite)")
            constring = self.__create_connection_string_sqlite()
            return create_engine(constring, echo=self.cfg.enable_echo)
        except Exception as exe:
            raise Exception(f"Error on db connect: {exe}")

    def __create_connection_string_mariadb(self, with_db: bool = True):
        dbtype = self.cfg.db_type
        datapath = f"{self.cfg.data_path}/{dbtype}"
        os.makedirs(datapath, exist_ok=True)
        dbname = self.cfg.db_name
        user = self.cfg.db_user
        password = self.cfg.db_pass
        host = self.cfg.db_host
        port = self.cfg.db_port
        if with_db is True:
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/"

    def __create_connection_string_sqlite(self):
        dbtype = self.cfg.db_type
        datapath = f"{self.cfg.data_path}/{dbtype}"
        os.makedirs(datapath, exist_ok=True)
        dbname = f"{self.cfg.db_name}.sqlite3"
        full = f"{datapath}/{dbname}"
        constring = f"sqlite:///{full}"
        return constring

    def _create_api(self, engine: Engine, metadata: MetaData):
        return DatabaseApi(engine, metadata)

    async def connect(self) -> bool:
        """Connects all databases"""
        if self.connected is False:
            self.initialize()
            self.api.connect()
            self.connected = True
            return self.connected
        return False

    async def disconnect(self) -> bool:
        """Disconnect all databases"""
        if self.connected is True:
            self.api.disconnect()
            self.connected = False
            return True
        return False

    # async def migrate_database(self):
    #     """Migrates data from one db to another"""
    #     from daas_web.common.request_context import get_context
    #
    #     ctx = get_context()
    #     dbase = await ctx.get_database()
    #     oldfiles = await dbase.get_all_files(0)
    #     oldapps = await dbase.get_all_applications(0)
    #     limits = await dbase.get_all_limits()
    #     objs = await dbase.all_daas_objects()
    #     envs = await dbase.all_environments()
    #     insts = await dbase.all_instances()
    #     cons = await dbase.all_connections()
    #
    #     if self.api is not None:
    #         for limit in limits:
    #             await self.api.db_session_upsert(limit)
    #         for obj in objs:
    #             await self.api.db_session_upsert(obj)
    #         for file in oldfiles:
    #             await self.api.db_session_upsert(file)
    #         for app in oldapps:
    #             await self.api.db_session_upsert(app)
    #         for env in envs:
    #             await self.api.db_session_upsert(env)
    #         for con in cons:
    #             await self.api.db_session_upsert(con)
    #         for inst in insts:
    #             await self.api.db_session_upsert(inst)
