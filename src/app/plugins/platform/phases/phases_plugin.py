"""Phases plugin"""

from app.plugins.platform.phases.phases_backend import PhasesBackend
from app.plugins.platform.phases.phases_tasks import (
    PhasesTask,
    baseimage_clone,
    baseimage_clone_from_app,
    baseimage_create,
    baseimage_create_from_app,
    baseimage_delete,
    baseimage_finalize,
    baseimage_list,
    baseimage_start,
    baseimage_status,
    baseimage_stop,
)
from app.plugins.platform.phases.phases_tasks_config import (
    ConfigurationTask,
    cfg_applist,
    cfg_from_app,
    cfg_set_target,
    cfg_tasklist,
)
from app.plugins.platform.phases.phases_tasks_env import (
    EnvironmentTask,
    environment_create,
    environment_delete,
    environment_finalize,
    environment_get,
    environment_run,
    environment_start,
    environment_stop,
    environments_get,
)
from app.plugins.platform.phases.enums import PhasesSystemTask
from app.plugins.platform.phases.phases_tasks_sys import (
    run_task_app_clone,
    run_task_app_create,
    run_task_connection_config,
    run_task_postboot,
    run_task_wait_for_inst,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.platform.phases.phases_routes import handler


class PhasesPlugin(PluginBase):
    """Phases plugin"""

    def __init__(
        self,
    ):
        self.backend = PhasesBackend()
        self.objlayer = None
        self.systasks = [
            (PhasesSystemTask.PHASES_POSTBOOT_ACTIONS.value, run_task_postboot),
            (PhasesSystemTask.PHASES_CREATE_FROM_APP.value, run_task_app_create),
            (PhasesSystemTask.PHASES_CLONE_FROM_APP.value, run_task_app_clone),
            (PhasesSystemTask.PHASES_WAIT_FOR_INSTANCE.value, run_task_wait_for_inst),
            (
                PhasesSystemTask.PHASES_CONFIGURE_CONNECTION.value,
                run_task_connection_config,
            ),
        ]
        self.apitasks = [
            (
                PhasesTask.PHASES_BASEIMAGE_CREATE_FROM_APP.value,
                baseimage_create_from_app,
            ),
            (
                PhasesTask.PHASES_BASEIMAGE_CLONE_FROM_APP.value,
                baseimage_clone_from_app,
            ),
            (PhasesTask.PHASES_BASEIMAGE_CREATE.value, baseimage_create),
            (PhasesTask.PHASES_BASEIMAGE_CLONE.value, baseimage_clone),
            (PhasesTask.PHASES_BASEIMAGE_FINALIZE.value, baseimage_finalize),
            (PhasesTask.PHASES_BASEIMAGE_DELETE.value, baseimage_delete),
            (PhasesTask.PHASES_BASEIMAGE_START.value, baseimage_start),
            (PhasesTask.PHASES_BASEIMAGE_STOP.value, baseimage_stop),
            (PhasesTask.PHASES_BASEIMAGE_STATUS.value, baseimage_status),
            (PhasesTask.PHASES_BASEIMAGE_LIST.value, baseimage_list),
            (EnvironmentTask.PHASES_ENV_CREATE.value, environment_create),
            (EnvironmentTask.PHASES_ENV_GET.value, environment_get),
            (EnvironmentTask.PHASES_ENVS_GET.value, environments_get),
            (EnvironmentTask.PHASES_ENV_DELETE.value, environment_delete),
            (EnvironmentTask.PHASES_ENV_RUN.value, environment_run),
            (EnvironmentTask.PHASES_ENV_START.value, environment_start),
            (EnvironmentTask.PHASES_ENV_STOP.value, environment_stop),
            (EnvironmentTask.PHASES_ENV_FINALIZE.value, environment_finalize),
            (ConfigurationTask.PHASES_CFG_SET_TARGET.value, cfg_set_target),
            (ConfigurationTask.PHASES_CFG_APPLIST.value, cfg_applist),
            (ConfigurationTask.PHASES_CFG_TASKLIST.value, cfg_tasklist),
            (ConfigurationTask.PHASES_CFG_FROM_APP.value, cfg_from_app),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Platform,
            False,
            backends=[self.backend],
            layers=[],
            handlers=self.handlers,
            apitasks=self.apitasks,
            systasks=self.systasks,
            authenticator=None,
            taskmanager=None,
        )

    async def plugin_start(self) -> bool:
        """Starts plugin"""
        return await self.backend.connect()

    async def plugin_stop(self) -> bool:
        """Stops plugin"""
        return await self.backend.disconnect()
