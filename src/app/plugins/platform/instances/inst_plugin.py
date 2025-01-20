"""Instance plugin"""

from app.plugins.platform.instances.inst_backend import InstanceBackend
from app.plugins.platform.instances.inst_tasks import (
    InstanceTask,
    vminvoke_action,
    vminvoke_app,
    vminvoke_cmd,
    vminvoke_filesystem,
    vminvoke_list,
    vminvoke_ospackage,
    vminvoke_resolution,
    vminvoke_rtt,
    vminvoke_ssh,
    vminvoke_test_icmp,
    vminvoke_test_ssh,
    vminvoke_upload,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.platform.instances.inst_routes import handler


class InstancePlugin(PluginBase):
    """Instance plugin"""

    def __init__(
        self,
    ):
        self.backend = InstanceBackend()
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (InstanceTask.INST_VMINVOKE_APP.value, vminvoke_app),
            (InstanceTask.INST_VMINVOKE_CMD.value, vminvoke_cmd),
            (InstanceTask.INST_VMINVOKE_SSH.value, vminvoke_ssh),
            (InstanceTask.INST_VMINVOKE_ACTION.value, vminvoke_action),
            (InstanceTask.INST_VMINVOKE_RESOLUTION.value, vminvoke_resolution),
            (InstanceTask.INST_VMINVOKE_OSPACKAGE.value, vminvoke_ospackage),
            (InstanceTask.INST_VMINVOKE_UPLOAD.value, vminvoke_upload),
            (InstanceTask.INST_VMINVOKE_FILESYSTEM.value, vminvoke_filesystem),
            (InstanceTask.INST_VMINVOKE_LIST.value, vminvoke_list),
            (InstanceTask.INST_VMINVOKE_TEST_ICMP.value, vminvoke_test_icmp),
            (InstanceTask.INST_VMINVOKE_TEST_SSH.value, vminvoke_test_ssh),
            (InstanceTask.INST_VMINVOKE_RTT.value, vminvoke_rtt),
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
