""" Database components"""

from enum import Enum
from typing import Any, Optional
from app.qweb.common.enums import ScheduledTaskFilter
from app.qweb.common.qweb_tools import get_service
from app.qweb.service.service_tasks import QwebTaskManager
from app.qweb.service.service_context import (
    LayerObject,
    QwebObjectLayer,
    ServiceComponent,
)


class ServiceObject(Enum):
    """Testplugin object type"""

    TASK = "task"
    TASKFILTER = "taskfilter"
    TASKLIST = "tasklist"
    TASKSTATUS = "taskstatus"


class ServiceObjectLayer(QwebObjectLayer):
    """Objectlayer for service objects"""

    async def get_object(self, obj: LayerObject, args: dict) -> Optional[Any]:
        """Retrieves entity from service component"""
        result = None
        mancomp = await get_service(ServiceComponent.TASK, QwebTaskManager)

        if obj.objtype == ServiceObject.TASK.value:
            taskid = args["id_task"]
            state = "all"
            result = await mancomp.get_scheduled_task(
                ScheduledTaskFilter.ALL, taskid, "", ""
            )
            self._log_info(f"fetched task by id: {result}")
        elif obj.objtype == ServiceObject.TASKSTATUS.value:
            result = await mancomp.get_status_scheduled_task()
            self._log_info(f"fetched task status: {result}")
        elif obj.objtype == ServiceObject.TASKFILTER.value:
            taskid = args["id_task"]
            objectid = args["id_object"]
            instid = args["id_instance"]
            state = "running"
            result = await mancomp.get_scheduled_task(
                ScheduledTaskFilter.RUNNING, taskid, objectid, instid
            )
            self._log_info(f"fetched filtered task: {result}")
        elif obj.objtype == ServiceObject.TASKLIST.value:
            objectid = args["id_object"]
            instid = args["id_instance"]
            state = args["state"]
            unfiltered = await mancomp.get_scheduled_tasks(state)
            result = {}
            if len(unfiltered.keys()) > 0:
                for name, val in unfiltered.items():
                    if objectid == "" and instid == "":
                        result[name] = val.to_json()
                        continue
                    if objectid != "" and instid != "":
                        if objectid == val.id_object and instid == val.id_instance:
                            result[name] = val.to_json()
                            continue
                    else:
                        if objectid != "":
                            if objectid == val.id_object:
                                result[name] = val.to_json()
                                continue
                        if instid != "":
                            if instid == val.id_instance:
                                result[name] = val.to_json()
                                continue
            self._log_info(f"fetched tasklist: {result}")
            return result
        else:
            self._log_error(f"Unknown object type: {obj.objtype}")
        if result is not None:
            self.objects_returned += 1
        return result
