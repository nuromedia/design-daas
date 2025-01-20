"""Repository components reflecting database tables"""

from typing import Optional, TypeVar, Type
from sqlalchemy import TextClause, text
from app.daas.common.enums import BackendName
from app.daas.common.model import (
    Application,
    DaaSEntity,
    DaasObject,
    Environment,
    File,
    GuacamoleConnection,
    RessourceInfo,
)
from app.daas.db.db_api import DatabaseApi
from app.daas.db.db_manager import DatabaseManager
from app.daas.db.db_model import Colnames, ORMEntity, ORMObject, Tablenames
from app.daas.objects.object_application import ApplicationObject
from app.daas.objects.object_instance import InstanceObject
from app.plugins.core.db.db_backend import DatabaseBackend
from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.service.service_runtime import get_qweb_runtime

T = TypeVar("T", bound="DaaSEntity")


class RepositoryBase(Loggable):
    """Grants access to a certain part of teh database"""

    def __init__(self):
        Loggable.__init__(self, LogTarget.DB)
        self.dbman = None
        self.connected = False

    async def _get_manager(self) -> DatabaseManager:
        runtime = get_qweb_runtime()
        dbase = runtime.backends.get(BackendName.DB.value)
        assert dbase is not None
        if isinstance(dbase, DatabaseBackend) and dbase.component is not None:
            return dbase.component
        raise ValueError("DatabaseManager not available")

    async def _get_config(self, name: str) -> dict:
        runtime = get_qweb_runtime()
        return runtime._read_toml_file(name)

    async def _connect(self) -> bool:
        self.dbman = await self._get_manager()
        if self.dbman is not None:
            if self.dbman.connected is False:
                await self.dbman.connect()
            self.connected = self.dbman.connected
            if self.connected is True:
                return self.connected
        raise SystemError("DB manager is not ready")

    async def _disconnect(self) -> bool:
        if self.dbman is not None:
            if self.dbman.connected is True:
                await self.dbman.disconnect()
            self.connected = self.dbman.connected
            return True
        raise SystemError("DB manager is not ready")

    async def _get_api(self) -> DatabaseApi:
        if self.dbman is not None and self.dbman.connected:
            if self.dbman.api is not None and self.dbman.api.connected:
                return self.dbman.api
        raise SystemError("DB api is not ready")

    async def _upsert(self, model: DaaSEntity) -> bool:
        api = await self._get_api()
        return await api.db_session_upsert(model)

    async def _select(
        self, name: Tablenames, filter: Optional[TextClause] = None
    ) -> list[ORMEntity]:
        api = await self._get_api()
        return await api.db_session_select(name, filter)

    async def _select_all(self, name: Tablenames) -> list[ORMEntity]:
        api = await self._get_api()
        return await api.db_session_select_all(name)

    async def _select_one(
        self, name: Tablenames, filter: Optional[TextClause] = None
    ) -> Optional[ORMEntity]:
        api = await self._get_api()
        return await api.db_session_select_one(name, filter)

    async def _select_max(
        self, name: Tablenames, colname_int: Colnames
    ) -> Optional[ORMEntity]:
        api = await self._get_api()
        return await api.db_session_select_max(name, colname_int)

    async def _delete(self, orm: Optional[DaaSEntity]) -> bool:
        api = await self._get_api()
        return await api.db_session_delete(orm) if orm is not None else False

    async def _get_filter_id(self, identifier: int | str) -> TextClause:
        return await self._get_filter_column(Colnames.Id, identifier)

    async def _get_filter_owner(self, id_owner: int | str) -> TextClause:
        return await self._get_filter_column(Colnames.Owner, id_owner)

    async def _get_filter_owner_shared(self, id_owner: int | str) -> TextClause:
        filter_shared = await self._get_filter_statement(Colnames.Owner, 0)
        filter_user = await self._get_filter_statement(Colnames.Owner, id_owner)
        return await self._get_filter_str(f"{filter_user} OR {filter_shared}")

    async def _get_filter_column(self, col: Colnames, val: int | str) -> TextClause:
        filter = await self._get_filter_statement(col, val)
        return await self._get_filter_str(filter)

    async def _get_filter_statement(self, col: Colnames, value: int | str) -> str:
        if isinstance(value, int):
            return f"{col.value} = {value}"
        if isinstance(value, str):
            return f"{col.value} = '{value}'"

    async def _get_filter_str(self, clause: str) -> TextClause:
        return text(clause)

    async def _to_orm(self, model: DaaSEntity, modeltype: Type[T]) -> Optional[T]:
        api = await self._get_api()
        result = await api.model_to_orm(model)
        if isinstance(result, modeltype):
            return result
        return None

    async def _to_model(self, orm: ORMEntity, modeltype: Type[T]) -> Optional[T]:
        api = await self._get_api()
        result = await api.orm_to_model(orm)
        if isinstance(result, modeltype):
            return result
        return None

    async def _to_model_list(
        self, ormlist: list[ORMEntity], modeltype: Type[T]
    ) -> list[T]:
        return [
            model
            for x in ormlist
            if (model := await self._to_model(x, modeltype)) is not None
        ]


class FileRepository(RepositoryBase):
    """Grants access to file table"""

    async def create_file(self, model: File):
        """Insert file"""
        return await self._upsert(model)

    async def update_file(self, model: File) -> bool:
        """Update file"""
        return await self._upsert(model)

    async def delete_file(self, id_pk: str) -> bool:
        """Remove file"""
        filter = await self._get_filter_id(id_pk)
        orm = await self._select_one(Tablenames.File, filter)
        model = await self._to_model(orm, File)
        return await self._delete(model)

    async def get_file(self, id_app: str) -> Optional[File]:
        """Fetch file by app id"""
        filter = await self._get_filter_id(id_app)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.File, filter)
        return await self._to_model(orm, File)

    async def get_all_files(self, id_owner: int) -> list[File]:
        """Fetch all available files"""
        filter = await self._get_filter_owner_shared(id_owner)
        selected = await self._select(Tablenames.File, filter)
        return await self._to_model_list(selected, File)

    async def get_user_files(self, id_owner: int) -> list[File]:
        """Fetch user files"""
        filter = await self._get_filter_owner(id_owner)
        selected = await self._select(Tablenames.File, filter)
        return await self._to_model_list(selected, File)

    async def get_shared_files(self) -> list[File]:
        """Fetch shared files"""
        filter = await self._get_filter_column(Colnames.Owner, 0)
        selected = await self._select(Tablenames.File, filter)
        return await self._to_model_list(selected, File)


class LimitRepository(RepositoryBase):
    """Grants access to limit table"""

    async def create_limit(self, model: RessourceInfo) -> bool:
        """Insert limit"""
        return await self._upsert(model)

    async def delete_limit(self, id_owner: int) -> bool:
        """Remove limit"""
        filter = await self._get_filter_owner(id_owner)
        orm = await self._select_one(Tablenames.Limit, filter)
        model = await self._to_model(orm, RessourceInfo)
        return await self._delete(model)

    async def get_limit(self, id_owner: int) -> Optional[RessourceInfo]:
        """Fetch limit by owner"""
        filter = await self._get_filter_owner(id_owner)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Limit, filter)
        return await self._to_model(orm, RessourceInfo)

    async def get_all_limits(self) -> list[RessourceInfo]:
        """Fetch all available limits"""
        selected = await self._select_all(Tablenames.Limit)
        return await self._to_model_list(selected, RessourceInfo)


class ApplicationRepository(RepositoryBase):
    """Grants access to application table"""

    async def create_application(self, model: ApplicationObject):
        """Insert application"""
        return await self._upsert(model)

    async def update_application(self, model: ApplicationObject) -> bool:
        """Update application"""
        return await self._upsert(model)

    async def delete_application(self, id_pk: str) -> bool:
        """Remove application"""
        filter = await self._get_filter_id(id_pk)
        orm = await self._select_one(Tablenames.Application, filter)
        model = await self._to_model(orm, ApplicationObject)
        return await self._delete(model)

    async def get_application(self, id_app: str) -> Optional[ApplicationObject]:
        """Fetch application by app id"""
        filter = await self._get_filter_id(id_app)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Application, filter)
        return await self._to_model(orm, ApplicationObject)

    async def get_all_applications(self, id_owner: int) -> list[ApplicationObject]:
        """Fetch all available applications"""
        filter = await self._get_filter_owner_shared(id_owner)
        selected = await self._select(Tablenames.Application, filter)
        return await self._to_model_list(selected, ApplicationObject)

    async def get_user_applications(self, id_owner: int) -> list[ApplicationObject]:
        """Fetch user applications"""
        filter = await self._get_filter_owner(id_owner)
        selected = await self._select(Tablenames.Application, filter)
        return await self._to_model_list(selected, ApplicationObject)

    async def get_shared_applications(self) -> list[ApplicationObject]:
        """Fetch shared applications"""
        filter = await self._get_filter_column(Colnames.Owner, 0)
        selected = await self._select(Tablenames.Application, filter)
        return await self._to_model_list(selected, ApplicationObject)


class ConnectionRepository(RepositoryBase):
    """Grants access to connections table"""

    async def create_guacamole_connection(self, model: GuacamoleConnection) -> bool:
        """Insert connection"""
        return await self._upsert(model)

    async def update_guacamole_connection(self, model: GuacamoleConnection) -> bool:
        """Update connection"""
        return await self._upsert(model)

    async def delete_connection(self, instance: InstanceObject) -> bool:
        """Remove connection"""
        id_con = ""
        if instance.id_con is not None:
            id_con = instance.id_con
            filter = await self._get_filter_id(id_con)
            orm = await self._select_one(Tablenames.Con, filter)
            model = await self._to_model(orm, GuacamoleConnection)
            return await self._delete(model)
        return False

    async def get_guacamole_connection(
        self, id_pk: str
    ) -> Optional[GuacamoleConnection]:
        """Fetch connection by id"""
        filter = await self._get_filter_id(id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Con, filter)
        return await self._to_model(orm, GuacamoleConnection)

    async def get_guacamole_connection_by_token(
        self, token: str
    ) -> Optional[GuacamoleConnection]:
        """Fetch connection by token"""
        filter = await self._get_filter_column(Colnames.ViewerToken, token)
        selected = await self._select_one(Tablenames.Con, filter)
        return await self._to_model(selected, GuacamoleConnection)

    async def all_connections(self) -> list[GuacamoleConnection]:
        """Fetch all available connections"""
        selected = await self._select_all(Tablenames.Con)
        return await self._to_model_list(selected, GuacamoleConnection)

    async def update_connection_protocol(
        self, connection: GuacamoleConnection
    ) -> Optional[GuacamoleConnection]:
        """Update connection"""
        id_con = connection.id
        filter = await self._get_filter_id(id_con)
        orm = await self._select_one(Tablenames.Con, filter)
        model = await self._to_model(orm, GuacamoleConnection)
        if model is not None:
            model.protocol = connection.protocol
            model.protocol = connection.protocol
            model.hostname = connection.hostname
            model.port = connection.port
            model.user = connection.user
            model.password = connection.password
            if await self._upsert(model) is True:
                return model
        return None


class EnvironmentRepository(RepositoryBase):
    """Grants access to environments table"""

    async def create_environment(self, model: Environment) -> bool:
        """Create environment"""
        return await self._upsert(model)

    async def update_environment(self, model: Environment) -> bool:
        """Update environment"""
        return await self._upsert(model)

    async def get_environment(self, id_pk: str) -> Optional[Environment]:
        """Fetch environment by id"""
        filter = await self._get_filter_id(id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Env, filter)
        return await self._to_model(orm, Environment)

    async def get_environments_by_object(self, obj_id: str) -> list[Environment]:
        """Fetch environment by name"""
        filter_id = await self._get_filter_statement(Colnames.ObjectId, obj_id)
        filter = await self._get_filter_str(filter_id)
        api = await self._get_api()
        ormlist = await api.db_session_select(Tablenames.Env, filter)
        return await self._to_model_list(ormlist, Environment)

    async def get_environment_by_name(
        self, obj_id: str, name: str
    ) -> Optional[Environment]:
        """Fetch environment by name"""
        filter_obj = await self._get_filter_statement(Colnames.ObjectId, obj_id)
        filter_name = await self._get_filter_statement(Colnames.Name, name)
        filter = await self._get_filter_str(f"{filter_name} AND {filter_obj}")
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Env, filter)
        return await self._to_model(orm, Environment)

    async def get_environment_by_backend_id(self, obj_id: str) -> Optional[Environment]:
        """Fetch environment state from its backend id"""
        filter = await self._get_filter_column(Colnames.BackendId, obj_id)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Env, filter)
        return await self._to_model(orm, Environment)

    async def all_environments(self) -> list[Environment]:
        """Fetch all available envs"""
        selected = await self._select_all(Tablenames.Env)
        return await self._to_model_list(selected, Environment)

    async def all_object_environments(self, id_env: str) -> list[Environment]:
        """Fetch all available envs"""
        flt = await self._get_filter_id(id_env)
        selected = await self._select(Tablenames.Env, flt)
        return await self._to_model_list(selected, Environment)

    async def delete_environment(self, env: Environment) -> bool:
        """Remove environment"""
        filter = await self._get_filter_id(env.id)
        orm = await self._select_one(Tablenames.Env, filter)
        model = await self._to_model(orm, Environment)
        return await self._delete(model)


class ObjectRepository(RepositoryBase):
    """Grants access to object table"""

    async def create_daas_object(self, model: DaasObject) -> bool:
        """Create object"""
        return await self._upsert(model)

    async def update_daas_object(self, model: DaasObject) -> bool:
        """Update object"""
        return await self._upsert(model)

    async def get_daas_object(self, id_pk: str) -> Optional[DaasObject]:
        """Fetch object by id"""

        filter = await self._get_filter_id(id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Obj, filter)
        return await self.__convert_by_object_type(orm)

    async def get_daas_object_by_docker_id(
        self, id_docker: str
    ) -> Optional[DaasObject]:
        """Fetch object by docker id"""
        filter_id = await self._get_filter_statement(Colnames.DockerId, id_docker)
        filter = await self._get_filter_str(filter_id)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Obj, filter)
        return await self.__convert_by_object_type(orm)

    async def get_daas_object_by_proxmox_id(
        self, id_proxmox: str
    ) -> Optional[DaasObject]:
        """Fetch object by proxmox id"""
        filter_id = await self._get_filter_statement(Colnames.ProxmoxId, id_proxmox)
        filter = await self._get_filter_str(filter_id)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Obj, filter)
        return await self.__convert_by_object_type(orm)

    async def get_daas_objects_by_owner(self, id_owner: int) -> list[DaasObject]:
        """Fetch all objects"""
        filter = await self._get_filter_owner(id_owner)
        api = await self._get_api()
        ormlist = await api.db_session_select(Tablenames.Obj, filter)
        return await self._to_model_list(ormlist, DaasObject)

    async def get_daas_objects_available(self, id_owner: int) -> list[DaasObject]:
        """Fetch all objects"""
        filter_obj = await self._get_filter_statement(Colnames.Owner, id_owner)
        filter_name = await self._get_filter_statement(Colnames.Owner, 0)
        filter = await self._get_filter_str(f"{filter_name} OR {filter_obj}")
        api = await self._get_api()
        ormlist = await api.db_session_select(Tablenames.Obj, filter)
        return await self.__convert_by_object_types(ormlist)

    async def all_daas_objects(self) -> list[DaasObject]:
        """Fetch all available objects"""
        ormlist = await self._select_all(Tablenames.Obj)
        return await self.__convert_by_object_types(ormlist)

    async def delete_daas_object(self, obj: DaasObject) -> bool:
        """Remove object"""
        filter = await self._get_filter_id(obj.id)
        orm = await self._select_one(Tablenames.Obj, filter)
        model = await self.__convert_by_object_type(orm)
        return await self._delete(model)

    async def suggest_vmid(self) -> int:
        """
        Suggests new vmid for a new virtual machine.
        Must be unique and between 100 and 254.
        """
        orm = await self._select_max(Tablenames.Obj, Colnames.ProxmoxId)
        if orm is None:
            return 100
        model = await self._to_model(orm, DaasObject)
        if model is None:
            self._log_info(f"Error converting orm to model: {orm}")
            return -1
        if model.id_proxmox < 100:
            self._log_info(f"Error invalid vmid found: {model.id_proxmox}")
            return -1
        if model.id_proxmox >= 100 and model.id_proxmox < 254:
            return model.id_proxmox + 1
        self._log_info("Not enough proxmox ids left")
        return -1

    async def __convert_by_object_type(self, orm: ORMEntity) -> Optional[DaasObject]:
        from app.daas.objects.object_container import ContainerObject
        from app.daas.objects.object_machine import MachineObject

        if orm is not None and isinstance(orm, ORMObject):
            if orm.object_type == "vm":
                return await self._to_model(orm, MachineObject)
            elif orm.object_type == "container":
                contmodel = await self._to_model(orm, DaasObject)
                if contmodel is not None:
                    contmodel = ContainerObject(**contmodel.get_data())
                    return contmodel
        return None

    async def __convert_by_object_types(
        self, ormlist: list[ORMEntity]
    ) -> list[DaasObject]:

        result = []
        for orm in ormlist:
            result.append(await self.__convert_by_object_type(orm))
        return result


class InstanceRepository(RepositoryBase):
    """Grants access to instance table"""

    async def create_instance(self, model: InstanceObject) -> bool:
        """Create instance"""
        return await self._upsert(model)

    async def update_instance(self, model: InstanceObject) -> bool:
        """Update instance"""

        model.app = await self._to_orm(model.app, ORMObject)
        return await self._upsert(model)

    async def all_instances(self) -> list[InstanceObject]:
        """Fetch all available instances"""
        selected = await self._select_all(Tablenames.Inst)
        return await self._to_model_list(selected, InstanceObject)

    async def get_instance_by_id(self, id_pk: str) -> Optional[InstanceObject]:
        """Fetch all instances"""
        filter = await self._get_filter_id(id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Inst, filter)
        # print(f"INSTBYID_BEFORE: {id_pk} {filter}")
        inst = await self._to_model(orm, InstanceObject)
        # print(f"INSTBYID_AFTER: {inst} {type(inst.app)}")
        return inst

    async def get_instance_by_objid(self, id_pk: str) -> Optional[InstanceObject]:
        """Fetch instances by object id"""
        filter = await self._get_filter_column(Colnames.AppId, id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Inst, filter)
        if orm is not None:
            # print(f"ORM: {orm} {type(orm.app)} {id_pk} {filter}")
            return await self._to_model(orm, InstanceObject)
        return None

    async def get_instance_by_envid(self, id_pk: str) -> Optional[InstanceObject]:
        """Fetch instances by environment id"""
        filter = await self._get_filter_column(Colnames.EnvId, id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Inst, filter)
        return await self._to_model(orm, InstanceObject)

    async def get_instance_by_conid(self, id_pk: str) -> Optional[InstanceObject]:
        """Fetch instances by connection id"""
        filter = await self._get_filter_column(Colnames.ConnectionId, id_pk)
        api = await self._get_api()
        orm = await api.db_session_select_one(Tablenames.Inst, filter)
        return await self._to_model(orm, InstanceObject)

    async def get_instances_by_owner(self, id_owner: int = 0) -> list[InstanceObject]:
        """Fetch all instances by owner id"""
        api = await self._get_api()
        flt = await self._get_filter_owner(id_owner)
        ormlist = await api.db_session_select(Tablenames.Inst, flt)
        return await self._to_model_list(ormlist, InstanceObject)

    async def get_instance_by_adr(self, adr: str) -> Optional[InstanceObject]:
        """Fetch all instances by ip address"""
        api = await self._get_api()
        flt_host = await self._get_filter_statement(Colnames.Host, adr)
        flt = await self._get_filter_str(flt_host)
        ormlist = await api.db_session_select_one(Tablenames.Inst, flt)
        return await self._to_model(ormlist, InstanceObject)

    async def get_instances_available(self, id_owner: int = 0) -> list[InstanceObject]:
        """Fetch all available instances"""
        api = await self._get_api()
        filter_obj = await self._get_filter_statement(Colnames.Owner, id_owner)
        filter_name = await self._get_filter_statement(Colnames.Owner, 0)
        filter = await self._get_filter_str(f"{filter_name} OR {filter_obj}")
        ormlist = await api.db_session_select(Tablenames.Inst, filter)
        return await self._to_model_list(ormlist, InstanceObject)

    async def delete_instance(self, instance: InstanceObject) -> bool:
        """Remove instance"""
        filter = await self._get_filter_id(instance.id)
        orm = await self._select_one(Tablenames.Inst, filter)
        model = await self._to_model(orm, InstanceObject)
        return await self._delete(model)
