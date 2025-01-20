"""Admin plugin"""

from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.resources.admin.admin_backend import AdminBackend
from app.plugins.resources.admin.admin_routes import handler
from app.plugins.resources.admin.admin_tasks import (
    AdminTask,
    admin_assign_app,
    admin_assign_obj_to_user,
    admin_monitoring_info,
    admin_monitoring_info_apps,
    admin_monitoring_info_files,
    admin_monitoring_info_host,
    admin_monitoring_info_limits,
    admin_monitoring_info_objects,
    admin_monitoring_info_sockets,
    admin_monitoring_info_tasks,
    admin_monitoring_info_utilization,
    admin_task_stop,
    admin_tasklist,
)


class AdminPlugin(PluginBase):
    """Admin plugin"""

    def __init__(self):
        self.backend = AdminBackend()
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (AdminTask.ADMIN_MONITORING.value, admin_monitoring_info),
            (
                AdminTask.ADMIN_MONITORING_TASKS.value,
                admin_monitoring_info_tasks,
            ),
            (AdminTask.ADMIN_MONITORING_APPS.value, admin_monitoring_info_apps),
            (
                AdminTask.ADMIN_MONITORING_FILES.value,
                admin_monitoring_info_files,
            ),
            (
                AdminTask.ADMIN_MONITORING_SOCKETS.value,
                admin_monitoring_info_sockets,
            ),
            (AdminTask.ADMIN_MONITORING_HOST.value, admin_monitoring_info_host),
            (
                AdminTask.ADMIN_MONITORING_OBJECTS.value,
                admin_monitoring_info_objects,
            ),
            (
                AdminTask.ADMIN_MONITORING_LIMITS.value,
                admin_monitoring_info_limits,
            ),
            (
                AdminTask.ADMIN_MONITORING_UTILIZATION.value,
                admin_monitoring_info_utilization,
            ),
            (
                AdminTask.ADMIN_ASSIGN_OBJ_TO_USER.value,
                admin_assign_obj_to_user,
            ),
            (
                AdminTask.ADMIN_ASSIGN_APP.value,
                admin_assign_app,
            ),
            (
                AdminTask.ADMIN_TASK_LIST.value,
                admin_tasklist,
            ),
            (
                AdminTask.ADMIN_TASK_STOP.value,
                admin_task_stop,
            ),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Late,
            False,
            backends=[self.backend],
            layers=[],
            handlers=self.handlers,
            systasks=self.systasks,
            apitasks=self.apitasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
