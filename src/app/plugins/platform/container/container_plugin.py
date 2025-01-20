"""Container plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.container.docker.DockerRequest import (
    DockerRequestConfig,
    DockerServicesConfig,
)
from app.plugins.platform.container.container_backend import ContainerBackend
from app.plugins.platform.container.container_routes import handler
from app.plugins.platform.container.container_tasks import (
    ContainerTask,
    container_list,
    container_logs,
    container_start,
    container_stop,
    daemon_info,
    image_build,
    image_clone,
    image_create,
    image_create_root,
    image_delete,
    image_inspect,
    image_list,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase


class ContainerPlugin(PluginBase):
    """Container plugin"""

    def __init__(
        self,
    ):
        cfgfile_db = self.read_toml_file(ConfigFile.CONTAINER)
        self.cfg_request = DockerRequestConfig(
            **cfgfile_db[ConfigSections.CONTAINER_REQUEST.value]
        )
        self.cfg_services = DockerServicesConfig(
            **cfgfile_db[ConfigSections.CONTAINER_SERVICES.value]
        )
        self.backend = ContainerBackend(self.cfg_request, self.cfg_services)
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (ContainerTask.CONT_DAEMON_INFO.value, daemon_info),
            (ContainerTask.CONT_IMAGE_INSPECT.value, image_inspect),
            (ContainerTask.CONT_IMAGE_BUILD.value, image_build),
            (ContainerTask.CONT_IMAGE_DELETE.value, image_delete),
            (ContainerTask.CONT_IMAGE_LIST.value, image_list),
            (ContainerTask.CONT_START.value, container_start),
            (ContainerTask.CONT_STOP.value, container_stop),
            (ContainerTask.CONT_LIST.value, container_list),
            (ContainerTask.CONT_LOG.value, container_logs),
            (ContainerTask.CONT_IMAGE_CREATE.value, image_create),
            (ContainerTask.CONT_IMAGE_CREATE_ROOT.value, image_create_root),
            (ContainerTask.CONT_IMAGE_CLONE.value, image_clone),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Early,
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
