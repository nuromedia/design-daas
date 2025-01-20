"""Database model objects"""

from enum import Enum
import logging
import json
from typing import List, Optional, Type
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy import BigInteger, ForeignKey, String, Table
from sqlalchemy.types import Text, TypeDecorator
from app.daas.common.model import DaaSEntity
from app.daas.db.db_mappings import (
    ORMMappingType,
    ORMModelPersistance,
    TableEntityMapping,
)
from app.qweb.logging.logging import LogTarget, Loggable


class Tablenames(Enum):
    """Enum with configured tablenames"""

    Obj = "daas_objects"
    Con = "guacamole_connections"
    File = "files"
    Application = "template_applications"
    Env = "environments"
    Inst = "instances"
    Limit = "limits"


class Colnames(Enum):
    """Enum with configured column names"""

    Id = "id"
    Name = "name"
    ObjectId = "id_object"
    BackendId = "id_backend"
    AppId = "id_app"
    EnvId = "id_env"
    ConnectionId = "id_con"
    DockerId = "id_docker"
    ProxmoxId = "id_proxmox"
    Owner = "id_owner"
    Host = "host"
    ViewerToken = "viewer_token"


class JsonType(TypeDecorator):
    """Wrapper to convert json objects into string"""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


Base = declarative_base()


class ORMEntity(Base, Loggable):
    """Baseclass for every orm-mapped object"""

    __abstract__ = True
    _logger: logging.Logger

    def __init__(self, **kwargs):
        Base.__init__(self)
        Loggable.__init__(self, LogTarget.DB)
        self.parentcls: Type[object] = self.__class__
        super(ORMEntity, self).__init__(**kwargs)

    def get_table(self) -> Optional[Table]:
        if self.__tablename__ in self.metadata.tables:
            return self.metadata.tables[self.__tablename__]
        return None

    def get_data(self, logme: bool = False):
        result = {k: v for k, v in self.__dict__.items() if k not in ORMEntity.__dict__}
        return self.clean_dict(result)

    def clean_dict(self, data: dict):
        if "_sa_instance_state" in data:
            data.pop("_sa_instance_state")
        if "__orminfo__" in data:
            data.pop("__orminfo__")
        return data

    def __repr__(self):
        data = self.get_data()
        clsname = self.__class__.__qualname__
        info = f"{clsname}("
        parts = []
        if "id" in data:
            parts.append(f"name={data['id']}")
        if "name" in data:
            parts.append(f"name={data['name']}")
        if "id_user" in data:
            parts.append(f"id_user={data['id_user']}")
        if "id_owner" in data:
            parts.append(f"owner={data['id_owner']}")
        if "os_type" in data:
            parts.append(f"os={data['os_type']}")
        if "object_type" in data:
            parts.append(f"type={data['object_type']}")
        if "instance" in data:
            parts.append(f"instance={data['instance']}")
        return f"{info}{','.join(parts)})"


@ORMModelPersistance(ORMMappingType.Object)
class ORMObject(ORMEntity):
    __tablename__ = "daas_objects"

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    instances: Mapped[List["ORMInstance"]] = relationship(
        back_populates="app", cascade="all, delete-orphan"
    )
    environments: Mapped[List["ORMEnvironment"]] = relationship(
        back_populates="app", cascade="all, delete-orphan"
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    id_user: Mapped[str] = mapped_column(String(128))
    id_owner: Mapped[int] = mapped_column()
    id_proxmox: Mapped[int] = mapped_column()
    id_docker: Mapped[str] = mapped_column(String(128))
    object_type: Mapped[str] = mapped_column(String(128))
    object_mode: Mapped[str] = mapped_column(String(128))
    object_mode_extended: Mapped[str] = mapped_column(String(128))
    object_state: Mapped[str] = mapped_column(String(1024))
    object_tasks: Mapped[JsonType] = mapped_column(JsonType)
    object_apps: Mapped[JsonType] = mapped_column(JsonType)
    object_target: Mapped[JsonType] = mapped_column(JsonType)
    object_storage: Mapped[str] = mapped_column(String(1024))
    os_type: Mapped[str] = mapped_column(String(32))
    os_wine: Mapped[str] = mapped_column(String(32))
    os_username: Mapped[str] = mapped_column(String(32))
    os_password: Mapped[str] = mapped_column(String(32))
    os_installer: Mapped[str] = mapped_column(String(4096))
    hw_cpus: Mapped[int] = mapped_column()
    hw_memory: Mapped[int] = mapped_column(BigInteger)
    hw_disksize: Mapped[int] = mapped_column(BigInteger)
    ceph_public: Mapped[int] = mapped_column()
    ceph_shared: Mapped[int] = mapped_column()
    ceph_user: Mapped[int] = mapped_column()
    vnc_port_system: Mapped[int] = mapped_column()
    vnc_port_instance: Mapped[int] = mapped_column()
    vnc_username: Mapped[str] = mapped_column(String(128))
    vnc_password: Mapped[str] = mapped_column(String(128))
    viewer_contype: Mapped[str] = mapped_column(String(32))
    viewer_resolution: Mapped[str] = mapped_column(String(32))
    viewer_resize: Mapped[str] = mapped_column(String(32))
    viewer_scale: Mapped[str] = mapped_column(String(32))
    viewer_dpi: Mapped[int] = mapped_column()
    viewer_colors: Mapped[int] = mapped_column()
    viewer_force_lossless: Mapped[int] = mapped_column()
    extra_args: Mapped[str] = mapped_column(String(128))


@ORMModelPersistance(ORMMappingType.Environment)
class ORMEnvironment(ORMEntity):
    __tablename__ = "environments"

    fk_objs = f"{Tablenames.Obj.value}.id"

    app: Mapped["ORMObject"] = relationship(back_populates="environments")
    inst: Mapped["ORMInstance"] = relationship(back_populates="env")

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    id_object: Mapped[str] = mapped_column(String(128), ForeignKey(fk_objs))
    id_backend: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(128))
    state: Mapped[str] = mapped_column(String(128))
    env_tasks: Mapped[JsonType] = mapped_column(JsonType)
    env_apps: Mapped[JsonType] = mapped_column(JsonType)
    env_target: Mapped[JsonType] = mapped_column(JsonType)
    created_at: Mapped[str] = mapped_column(String(32))


@ORMModelPersistance(ORMMappingType.GuacamoleConnection)
class ORMGuacamoleConnection(ORMEntity):
    __tablename__ = "guacamole_connections"

    obj = relationship("ORMInstance", back_populates="con")

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    viewer_url: Mapped[str] = mapped_column(String(256))
    viewer_token: Mapped[str] = mapped_column(String(256))
    user: Mapped[str] = mapped_column(String(128))
    password: Mapped[str] = mapped_column(String(128))
    protocol: Mapped[str] = mapped_column(String(32))
    hostname: Mapped[str] = mapped_column(String(128))
    port: Mapped[int] = mapped_column()


@ORMModelPersistance(ORMMappingType.Instance)
class ORMInstance(ORMEntity):
    __tablename__ = "instances"

    def __init__(self, **kwargs):
        if "config_inst" in kwargs:
            kwargs.pop("config_inst")
        if "config_ssh" in kwargs:
            kwargs.pop("config_ssh")
        super().__init__(**kwargs)

    fk_objs = f"{Tablenames.Obj.value}.id"
    fk_envs = f"{Tablenames.Env.value}.id"
    fk_cons = f"{Tablenames.Con.value}.id"

    app: Mapped[ORMObject] = relationship(back_populates="instances")
    env: Mapped[Optional[ORMEnvironment]] = relationship(
        back_populates="inst",
        single_parent=True,
        # cascade="all, delete-orphan",
    )
    con: Mapped[Optional[ORMGuacamoleConnection]] = relationship(
        back_populates="obj",
        single_parent=True,
        cascade="all, delete-orphan",
    )

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    id_app: Mapped[str] = mapped_column(String(128), ForeignKey(fk_objs))
    id_env: Mapped[str] = mapped_column(String(128), ForeignKey(fk_envs), nullable=True)
    id_con: Mapped[str] = mapped_column(String(128), ForeignKey(fk_cons), nullable=True)
    id_owner: Mapped[int] = mapped_column()
    host: Mapped[str] = mapped_column(String(128), nullable=True)
    container: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32))
    connected_at: Mapped[str] = mapped_column(String(32))
    booted_at: Mapped[str] = mapped_column(String(32))


@ORMModelPersistance(ORMMappingType.File)
class ORMFile(ORMEntity):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    id_owner: Mapped[int] = mapped_column()
    os_type: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    version: Mapped[str] = mapped_column(String(128))
    localpath: Mapped[str] = mapped_column(String(1024))
    remotepath: Mapped[str] = mapped_column(String(1024))
    filesize: Mapped[int] = mapped_column()
    created_at: Mapped[str] = mapped_column(String(32))


@ORMModelPersistance(ORMMappingType.Application)
class ORMApplication(ORMEntity):
    __tablename__ = "template_applications"

    fk_files = f"{Tablenames.File.value}.id"
    fk_objs = f"{Tablenames.Obj.value}.id"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    id_owner: Mapped[int] = mapped_column()
    id_file: Mapped[str] = mapped_column(
        String(128), ForeignKey(fk_files), nullable=True
    )
    id_template: Mapped[str] = mapped_column(
        String(128), ForeignKey(fk_objs), nullable=True
    )
    os_type: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    installer: Mapped[str] = mapped_column(String(1024))
    installer_args: Mapped[str] = mapped_column(String(1024))
    installer_type: Mapped[str] = mapped_column(String(1024))
    target: Mapped[str] = mapped_column(String(1024))
    target_args: Mapped[str] = mapped_column(String(1024))
    version: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[str] = mapped_column(String(32))


@ORMModelPersistance(ORMMappingType.Limit)
class ORMLimit(ORMEntity):
    __tablename__ = "limits"

    id_owner: Mapped[int] = mapped_column(primary_key=True)
    vm_max: Mapped[int] = mapped_column()
    container_max: Mapped[int] = mapped_column()
    obj_max: Mapped[int] = mapped_column()
    cpu_max: Mapped[int] = mapped_column()
    mem_max: Mapped[int] = mapped_column(BigInteger)
    dsk_max: Mapped[int] = mapped_column(BigInteger)


def create_model(orm: ORMEntity) -> Optional[DaaSEntity]:
    """Converts orm object to model object"""

    if hasattr(orm, "__tablename__"):
        tabname: str = getattr(orm, "__tablename__")
        mappings = TableEntityMapping()
        mapped_cls = mappings.get_domain(tabname)
        if mapped_cls is not None:
            data = orm.get_data()
            data = check_data(orm, data)
            obj = mapped_cls(**data)
            if isinstance(obj, DaaSEntity):
                return obj


def check_data(orm: ORMEntity, data: dict) -> dict:
    from app.daas.objects.object_container import ContainerObject
    from app.daas.objects.object_machine import MachineObject

    if isinstance(orm, ORMInstance):
        testapp = getattr(orm, "app")
        testenv = getattr(orm, "env")
        for attr in vars(orm):
            val = getattr(orm, attr)
            if isinstance(val, ORMEntity):
                newval = create_model(val)
                if isinstance(val, ORMObject):
                    if newval is not None:
                        if val.object_type == "vm":
                            data[attr] = MachineObject(**newval.get_data())
                        else:
                            data[attr] = ContainerObject(**newval.get_data())
                else:
                    data[attr] = newval
    return data


def check_model_childs(model: dict) -> dict:

    for k, v in model.items():
        if isinstance(v, ORMEntity):
            print(f"Found child model {model}")
            sub = create_model(v)
            model[k] = sub
        if isinstance(v, List):
            newv = []
            for el in v:
                if isinstance(el, ORMEntity):
                    sub = create_orm(el)
                    newv.append(sub)
            model[k] = newv
    return model


def create_orm(model: DaaSEntity) -> Optional[ORMEntity]:
    """Converts model object to orm object"""
    if hasattr(model.__class__, "__orm_etype"):
        etype: ORMMappingType = getattr(model.__class__, "__orm_etype")
        mappings = TableEntityMapping()
        mapped_cls = mappings.get_orm(etype.table)
        if mapped_cls is not None:
            data = model.get_data()
            data = check_orm_childs(data)
            obj = mapped_cls(**data)
            if isinstance(obj, ORMEntity):
                return obj
    else:
        raise ValueError("Object is not persistable")


def check_orm_childs(orm: dict) -> dict:

    for k, v in orm.items():
        if isinstance(v, DaaSEntity):
            sub = create_orm(v)
            orm[k] = sub
        if isinstance(v, List):
            newv = []
            for el in v:
                if isinstance(el, DaaSEntity):
                    sub = create_orm(el)
                    newv.append(sub)
                else:
                    newv.append(el)
            orm[k] = newv
    return orm
