""" Database components"""

from enum import Enum
from typing import Optional
from app.daas.common.model import DaaSEntity
from app.daas.db.database import Database
from app.qweb.service.service_context import LayerObject, QwebObjectLayer


class DBObject(Enum):
    """Testplugin object type"""

    OBJ = "object"
    OBJBYINST = "object_by_inst"
    OBJBYAPP = "object_by_app"
    NEWOBJ = "newobject"
    INST = "instance"
    INSTBYID = "instance_by_id"
    INSTBYOBJ = "instance_by_obj"
    INSTBYQUERY = "instance_by_query"
    INSTLIST = "instancelist"
    ENV = "env"
    ENVBYOBJ = "envbyobj"
    FILE = "file"
    APP = "app"
    CON = "con"
    LIMIT = "limit"
    TASK = "task"


# pylint: disable=too-few-public-methods
class DatabaseObjectLayer(QwebObjectLayer):
    """DBlayer for objects"""

    async def get_object(self, obj: LayerObject, args: dict) -> Optional[DaaSEntity]:
        """Retrieves entity from db backend"""
        result = None
        db = Database()
        await db.connect()
        if db.connected:
            if obj.objtype == DBObject.OBJ.value:
                objectid = args["id"]
                result = await db.get_daas_object(objectid)
                # self._log_info(f"fetched object: {result}")
            elif obj.objtype == DBObject.OBJBYINST.value:
                objectid = args["id_instance"]
                inst = await db.get_instance_by_id(objectid)
                if inst is not None:
                    result = await db.get_daas_object(inst.app.id)
                # self._log_info(f"fetched object by id: {result}")
            elif obj.objtype == DBObject.NEWOBJ.value:
                objectid = args["newid"]
                result = await db.get_daas_object(objectid)
                # self._log_info(f"fetched object: {result}")
            elif obj.objtype == DBObject.INST.value:
                objectid = args["id_instance"]
                result = await db.get_instance_by_id(objectid)
                # self._log_info(f"fetched instance: {result}")
            elif obj.objtype == DBObject.INSTBYQUERY.value:
                objectid = args["id"]
                result = await db.get_instance_by_id(objectid)
                # self._log_info(f"fetched instance: {result}")
            elif obj.objtype == DBObject.INSTBYOBJ.value:
                objectid = args["id"]
                envid = args["id_env"]
                if envid is not None and envid == "":
                    result = await db.get_instance_by_objid(objectid)
                else:
                    env = await db.get_environment_by_name(objectid, envid)
                    if env is not None:
                        result = await db.get_instance_by_envid(env.id)
                # self._log_info(f"fetched instance: {result}")
            elif obj.objtype == DBObject.INSTBYID.value:
                objectid = args["id"]
                envid = args["id_env"]
                if envid is not None and envid == "":
                    result = await db.get_instance_by_objid(objectid)
                else:
                    result = await db.get_instance_by_envid(envid)
                # self._log_info(f"fetched instance: {result}")
            elif obj.objtype == DBObject.INSTLIST.value:
                result = await db.all_instances()
                self._log_info(f"fetched instancelist: {result}")
            elif obj.objtype == DBObject.ENV.value:
                objectid = args["id"]
                result = await db.get_environment(objectid)
                # self._log_info(f"fetched environment: {result}")
            elif obj.objtype == DBObject.ENVBYOBJ.value:
                objectid = args["id"]
                name = ""
                if "name" in args:
                    name = args["name"]
                elif "env" in args:
                    name = args["env"]
                if name != "":
                    result = await db.get_environment_by_name(objectid, name)
                    # self._log_info(f"fetched object environment: {result}")
            elif obj.objtype == DBObject.FILE.value:
                objectid = args["id"]
                result = await db.get_file(objectid)
                # self._log_info(f"fetched file: {result}")
            elif obj.objtype == DBObject.APP.value:
                objectid = ""
                if "appid" in args:
                    objectid = args["appid"]
                elif "id" in args:
                    objectid = args["id"]
                if objectid != "":
                    result = await db.get_application(objectid)
                # self._log_info(f"fetched app: {result}")
            elif obj.objtype == DBObject.OBJBYAPP.value:
                objectid = ""
                if "appid" in args:
                    objectid = args["appid"]
                if objectid != "":
                    app = await db.get_application(objectid)
                    if app is not None and app.id_template is not None:
                        result = await db.get_daas_object(app.id_template)
                # self._log_info(f"fetched app: {result}")
            elif obj.objtype == DBObject.CON.value:
                objectid = args["id"]
                result = await db.get_guacamole_connection(objectid)
                # self._log_info(f"fetched connection: {result}")
            elif obj.objtype == DBObject.LIMIT.value:
                objectid = int(args["id_owner"])
                result = await db.get_limit(objectid)
                # self._log_info(f"Layer fetched limit: {result}")
            else:
                self._log_error(f"Unknown object type: {obj.objtype}")
        if result is not None:
            self.objects_returned += 1
        return result
