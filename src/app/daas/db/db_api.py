"""Database api"""

from typing import Optional, Type
from sqlalchemy import Column, Engine, Table, TextClause, text
from sqlalchemy.orm import Query, Session
from sqlalchemy.schema import MetaData
from app.daas.common.model import DaaSEntity
from app.daas.db.db_model import (
    Colnames,
    ORMEntity,
    Tablenames,
    create_model,
    create_orm,
)
from app.daas.db.db_mappings import TableEntityMapping
from app.qweb.logging.logging import LogTarget, Loggable


class DatabaseApiBase(Loggable):
    """Baseclass for Database api"""

    def __init__(self):
        Loggable.__init__(self, LogTarget.DB)

    async def _get_table_pk(self, tab: Optional[Table]) -> Optional[Column]:
        if tab is not None:
            primary_key_columns = tab.primary_key.columns
            primary_key_column = list(primary_key_columns)[0]
            return primary_key_column
        return None

    async def _get_pk_column_name(
        self, tab: Optional[Table], pk: Optional[Column]
    ) -> str:
        if tab is not None and pk is not None:
            return pk.name.replace(f"{tab.name}.", "")
        return ""

    async def _get_table_mapping_orm(
        self, tab: Optional[Table]
    ) -> Optional[type[ORMEntity]]:
        mappings = TableEntityMapping()
        if tab is not None:
            mapping = mappings.get_orm(tab.name)
            if mapping is not None and issubclass(mapping, ORMEntity):
                return mapping
        return None

    async def _get_table_mapping_domain(self, tab: Table) -> Optional[type[DaaSEntity]]:
        mappings = TableEntityMapping()
        mapping = mappings.get_domain(tab.name)
        if mapping is not None and issubclass(mapping, DaaSEntity):
            return mapping
        return None


class DatabaseApi(DatabaseApiBase):
    """Handles calls to the database"""

    def __init__(self, engine: Engine, metadata: MetaData):
        super().__init__()
        self.engine = engine
        self.metadata = metadata
        self.connected = False

    def connect(self):
        """Creates new session"""
        self.session = Session(self.engine)
        self.connected = True

    def disconnect(self):
        """Closes session"""
        if self.session is not None:
            self.session.close()
            self.session = None
        self.connected = False

    async def orm_to_model(self, orm: ORMEntity):
        """Converts orm object to daas object"""
        return create_model(orm)

    async def model_to_orm(self, model: DaaSEntity):
        """Converts model object to orm object"""
        return create_orm(model)

    async def db_session_flush(
        self,
    ) -> bool:
        """Flush all changes to the db"""
        if self.session is None:
            return False
        self.session.flush()
        return True

    def db_session_create(
        self,
        dbname: str,
    ) -> bool:
        """Flush all changes to the db"""
        if self.session is None:
            return False
        with self.engine.connect() as connection:
            self._log_info(f"Create Database {dbname}")
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {dbname};"))
            connection.commit()
        return True

    async def db_session_query(
        self,
        mapping: Type,
        filter: Optional[TextClause] = None,
    ) -> Optional[Query]:
        """Query the session by using specified mapping"""
        if self.session is None:
            return None
        qresult = self.session.query(mapping)
        if filter is not None:
            qresult = qresult.filter(filter)
        return qresult

    async def db_session_upsert(self, model: DaaSEntity) -> bool:
        """Inserts or update given domain object"""
        orm = await self.model_to_orm(model)
        if orm is not None and self.session is not None:
            self._log_info(f"SQL (Upsert) {orm}")
            self.session.merge(orm)
            self.session.commit()
            return True
        return False

    async def db_session_delete(self, model: DaaSEntity) -> bool:
        """Delete specified domain object"""
        if self.session is None:
            return False
        tab: Optional[Table] = await self.get_table_by_domain(model)
        pk = await self._get_table_pk(tab)
        col = await self._get_pk_column_name(tab, pk)
        mapping = await self._get_table_mapping_orm(tab)
        data = model.get_data()
        if model is None or tab is None or pk is None or mapping is None:
            return False
        if col not in data:
            self._log_error(f"Column {col} not contained in {model.get_data()}")
            return False

        entity = self.session.query(mapping).filter(pk == data[col]).first()
        if entity:
            self._log_info(f"SQL (Delete) {entity}")
            self.session.delete(entity)
            self.session.commit()
        return True

    async def db_session_select_all(self, tablename: Tablenames) -> list[ORMEntity]:
        """Select all from specified table"""
        return await self.db_session_select(tablename)

    async def db_session_select_one(
        self, tablename: Tablenames, filter: Optional[TextClause] = None
    ) -> Optional[ORMEntity]:
        """Select one from specified table"""
        result = await self.db_session_select(tablename, filter)
        if len(result) >= 1:
            return result[0]
        return None

    async def db_session_select_max(
        self, tablename: Tablenames, column_int: Colnames
    ) -> Optional[ORMEntity]:
        """Select max value, from specified table and column"""
        mapping: Optional[Type[object]] = await self.get_mapping_orm(tablename.value)
        if mapping is None:
            return None
        flt = text(f"{column_int.value} > 0 ORDER BY {column_int.value} Desc")
        return await self.db_session_select_one(tablename, flt)

    async def db_session_select(
        self, tablename: Tablenames, filter: Optional[TextClause] = None
    ) -> list[ORMEntity]:
        """Select from specified table"""
        mapping: Optional[Type[object]] = await self.get_mapping_orm(tablename.value)
        if mapping is None:
            return []
        self._log_info(f"SQL (Select) {tablename}")
        qresult = await self.db_session_query(mapping, filter)
        if qresult is None:
            return []
        return [x for x in qresult if isinstance(x, ORMEntity)]

    async def get_table(self, name: str) -> Optional[Table]:
        """Returns associated table object if available"""
        if name in self.metadata.tables:
            return self.metadata.tables[name]
        return None

    async def get_table_by_orm(self, orm: ORMEntity) -> Optional[Table]:
        """Gets Table associated with specified orm type"""
        return orm.get_table()

    async def get_table_by_domain(self, model: DaaSEntity) -> Optional[Table]:
        """Gets Table associated with specified model type"""
        orm = await self.model_to_orm(model)
        if orm is not None:
            return orm.get_table()
        return None

    async def get_mapping_orm(self, name: str) -> Optional[ORMEntity]:
        """Get mapping orm"""
        tab: Optional[Table] = await self.get_table(name)
        return await self._get_table_mapping_orm(tab)

    async def get_mapping_domain(self, name: str) -> Optional[DaaSEntity]:
        """Get mapping orm"""
        tab: Optional[Table] = await self.get_table(name)
        return await self._get_table_mapping_orm(tab)
