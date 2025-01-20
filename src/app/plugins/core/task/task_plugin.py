"""Task plugin"""

from app.daas.common.enums import BackendName
from app.plugins.core.task.task_backend import TaskBackend
from app.plugins.core.task.task_layer import ServiceObjectLayer
from app.plugins.core.task.task_tasks import (
    TaskTask,
    task_get,
    task_list,
    task_status,
    task_stop,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.core.task.task_routes import handler


class TaskPlugin(PluginBase):
    """Taskplugin"""

    def __init__(
        self,
    ):
        self.backend = TaskBackend()
        self.obj_layer = ServiceObjectLayer(
            name=BackendName.TASK.value, backend=self.backend
        )
        self.systasks = []
        self.apitasks = [
            (TaskTask.TASK_GET.value, task_get),
            (TaskTask.TASK_STOP.value, task_stop),
            (TaskTask.TASK_LIST.value, task_list),
            (TaskTask.TASK_STATUS.value, task_status),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Core,
            False,
            backends=[self.backend],
            layers=[self.obj_layer],
            handlers=self.handlers,
            systasks=self.systasks,
            apitasks=self.apitasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return True

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return True
