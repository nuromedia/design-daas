"""VM plugin"""

from app.daas.common.enums import ConfigFile, ConfigSections
from app.daas.storage.filestore import FilestoreConfig
from app.plugins.storage.files.file_backend import FileBackend
from app.plugins.storage.files.file_tasks import (
    FileTask,
    app_create,
    app_create_shared,
    app_delete,
    app_delete_shared,
    app_get,
    app_list,
    app_update,
    app_update_shared,
    files_create,
    files_create_shared,
    files_delete,
    files_delete_shared,
    files_get,
    files_list,
    files_update,
    files_update_shared,
)
from app.qweb.service.service_plugin import LoadOrder, PluginBase
from app.plugins.storage.files.file_routes import handler


class FilePlugin(PluginBase):
    """File plugin"""

    def __init__(
        self,
    ):
        cfgfile_db = self.read_toml_file(ConfigFile.FILE)
        self.cfg_storage = FilestoreConfig(
            **cfgfile_db[ConfigSections.FILES_STORE.value]
        )
        self.backend = FileBackend(self.cfg_storage)
        self.objlayer = None
        self.systasks = []
        self.apitasks = [
            (FileTask.FILE_GET.value, files_get),
            (FileTask.FILE_DELETE.value, files_delete),
            (FileTask.FILE_DELETE_SHARED.value, files_delete_shared),
            (FileTask.FILE_LIST.value, files_list),
            (FileTask.FILE_CREATE.value, files_create),
            (FileTask.FILE_UPDATE.value, files_update),
            (FileTask.FILE_CREATE_SHARED.value, files_create_shared),
            (FileTask.FILE_UPDATE_SHARED.value, files_update_shared),
            (FileTask.APP_GET.value, app_get),
            (FileTask.APP_DELETE.value, app_delete),
            (FileTask.APP_DELETE_SHARED.value, app_delete_shared),
            (FileTask.APP_LIST.value, app_list),
            (FileTask.APP_CREATE.value, app_create),
            (FileTask.APP_UPDATE.value, app_update),
            (FileTask.APP_CREATE_SHARED.value, app_create_shared),
            (FileTask.APP_UPDATE_SHARED.value, app_update_shared),
        ]
        self.handlers = [handler]
        super().__init__(
            self.__class__.__qualname__,
            LoadOrder.Storage,
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
