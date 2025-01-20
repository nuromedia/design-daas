"""Database persistance objects"""

from enum import Enum
from collections import namedtuple
from typing import Optional, Type


TableMapping = namedtuple("TableMapping", ["id", "table"])


class ORMMappingType(Enum):
    Unknown = TableMapping(0, "")
    Object = TableMapping(1, "daas_objects")
    Machine = TableMapping(2, "daas_objects")
    Container = TableMapping(3, "daas_objects")
    File = TableMapping(4, "files")
    Application = TableMapping(5, "template_applications")
    Environment = TableMapping(6, "environments")
    Instance = TableMapping(7, "instances")
    GuacamoleConnection = TableMapping(8, "guacamole_connections")
    Limit = TableMapping(9, "limits")

    @property
    def id(self):
        return self.value.id

    @property
    def table(self):
        return self.value.table


def ORMModelDomain(etype: ORMMappingType):
    def decorator(cls):
        cls.__orm_etype = etype
        mappings = TableEntityMapping()
        mappings.add_mapping_domain(cls.__orm_etype.table, cls)
        return cls

    return decorator


def ORMModelPersistance(etype: ORMMappingType):
    def decorator(cls):
        cls.__orm_etype = etype
        mappings = TableEntityMapping()
        mappings.add_mapping_orm(cls.__orm_etype.table, cls)
        return cls

    return decorator


class TableEntityMapping:
    _instance = None
    _mappings_orm = None
    _mappings_domain = None
    _logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TableEntityMapping, cls).__new__(cls, *args, **kwargs)
            cls._instance._mappings_orm = {}
            cls._instance._mappings_domain = {}
        return cls._instance

    def add_mapping_orm(self, table, orm_entity):
        if self._mappings_orm is not None and table not in self._mappings_orm:
            self.__log_info(f"Adding orm {table} with {orm_entity}")
            self._mappings_orm[table] = orm_entity

    def add_mapping_domain(self, table, domain_entity):
        if self._mappings_domain is not None and table not in self._mappings_domain:
            self.__log_info(f"Adding mod {table} with {domain_entity}")
            self._mappings_domain[table] = domain_entity

    def get_orm(self, table) -> Optional[Type[object]]:
        if self._mappings_orm is not None and table in self._mappings_orm.keys():
            return self._mappings_orm[table]
        return None

    def get_domain(self, table) -> Optional[Type[object]]:
        if self._mappings_domain is not None and table in self._mappings_domain.keys():
            return self._mappings_domain[table]
        return None

    def __log_info(self, msg: str):
        print(f"Mappings: {msg}")
