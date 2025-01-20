"""
System information
"""

from dataclasses import asdict, dataclass
from typing import Optional
from app.daas.db.database import Database
from app.daas.resources.info.boardinfo import DashboardInfo, DashboardInfoStore
from app.daas.common.model import DaasObject
from app.daas.resources.info.hostinfo import HostRessources, Hostinfo
from app.daas.resources.info.config import SysteminfoConfig
from app.daas.resources.info.objectstats import (
    ObjectStats,
    SystemInfoDockerContainer,
    SystemInfoDockerImage,
    SystemInfoObjects,
    SystemInfoProxmoxMachine,
)
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class ObjectFilter:
    """Filter object to specify entities"""

    detailed: bool
    daas: bool
    user: int


@dataclass
class DaaSObjectResponse:
    """Daas Object response"""

    daas_id: str
    daas_type: str
    daas_owner: int
    daas_name: str
    daas_object: bool


class Systeminfo(Loggable):
    """
    Filestore to keep track of files
    """

    def __init__(self, config: SysteminfoConfig):
        Loggable.__init__(self, LogTarget.SYS)
        self.config = config
        self.objtool = ObjectStats()
        self.hosttool = Hostinfo()
        self.boardtool = DashboardInfoStore()
        self.current_objinfo: Optional[SystemInfoObjects] = None
        self.current_hostinfo: Optional[HostRessources] = None
        self.dbase = Database()

    async def initialize(self):
        """Initializes component"""
        await self.dbase.connect()
        await self.boardtool.initialize()

    async def get_dashboard_info(self, userid: int) -> DashboardInfo:
        """Dashboard info"""
        return await self.boardtool.get_dashboard_info(userid)

    async def synchronize_all_objects(self, detailed: bool) -> bool:
        """Synchronizes database with system wide containers and proxmox-vms"""
        self.current_hostinfo = await self.get_hostinfo()
        self.current_objinfo = await self.get_objinfo(detailed)
        return True

    async def get_hostinfo(self) -> Optional[HostRessources]:
        """Returns hostinfo"""
        self.current_hostinfo = await self.hosttool.read_host_ressources()
        return self.current_hostinfo

    async def get_objinfo(self, detailed: bool) -> SystemInfoObjects:
        """Returns objinfo"""
        self.current_objinfo = await self.objtool.create_object_info(detailed)
        return self.current_objinfo

    async def get_filtered_objectinfo(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> SystemInfoObjects:
        """Returns all objects"""
        user_vms = await self.filter_proxmox_vms(detailed, only_daas, only_user)
        user_docker_images = await self.filter_docker_images(
            detailed, only_daas, only_user
        )
        return SystemInfoObjects(user_vms, user_docker_images)

    async def get_all_objects(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[dict]:
        """Returns all objects"""
        user_vms = await self.get_all_proxmox_vms(detailed, only_daas, only_user)
        user_docker_images = await self.get_all_docker_images(
            detailed, only_daas, only_user
        )
        all_objects = user_vms
        all_objects.extend(user_docker_images)
        return all_objects

    # pylint: disable=import-outside-toplevel
    async def filter_proxmox_vms(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[SystemInfoProxmoxMachine]:
        """
        Lists all vms
        """
        result: list[SystemInfoProxmoxMachine] = []
        vmlist = await self.objtool.enumerate_vms(detailed)
        for single in vmlist:
            obj = await self.dbase.get_daas_object_by_proxmox_id(str(single.id_object))
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_vms
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(single)
        return result

    async def filter_docker_images(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[SystemInfoDockerImage]:
        """
        Lists all docker images
        """
        result: list[SystemInfoDockerImage] = []
        contlist = await self.objtool.enumerate_container(detailed)
        imagelist = await self.objtool.enumerate_images(contlist, detailed)
        for single in imagelist:
            obj = await self.dbase.get_daas_object_by_docker_id(single.name)
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_images
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(single)
        return result

    async def filter_docker_containers(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[SystemInfoDockerContainer]:
        """
        Lists all docker containers
        """
        result: list[SystemInfoDockerContainer] = []
        containerlist = await self.objtool.enumerate_container(detailed)
        for single in containerlist:
            obj = await self.dbase.get_daas_object_by_docker_id(single.name)
            if obj is None:
                env = await self.dbase.get_environment_by_backend_id(single.name)
                if env is not None:
                    obj = await self.dbase.get_daas_object(env.id_object)
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_containers
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(single)
        return result

    # pylint: disable=import-outside-toplevel
    async def get_all_proxmox_vms(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[dict]:
        """
        Lists all vms
        """
        result: list[dict] = []
        vmlist = await self.objtool.enumerate_vms(detailed)
        for single in vmlist:
            obj = await self.dbase.get_daas_object_by_proxmox_id(str(single.id_object))
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_vms
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(asdict(resp))
        return result

    async def get_all_docker_images(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[dict]:
        """
        Lists all docker images
        """
        result: list[dict] = []
        contlist = await self.objtool.enumerate_container(detailed)
        imagelist = await self.objtool.enumerate_images(contlist, detailed)
        for single in imagelist:
            obj = await self.dbase.get_daas_object_by_docker_id(single.name)
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_images
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(asdict(resp))
        return result

    async def get_all_docker_containers(
        self,
        detailed: bool = False,
        only_daas: bool = False,
        only_user: int = -1,
    ) -> list[dict]:
        """
        Lists all docker containers
        """
        result: list[dict] = []
        containerlist = await self.objtool.enumerate_container(detailed)
        for single in containerlist:
            obj = await self.dbase.get_daas_object_by_docker_id(single.name)
            if obj is None:
                env = await self.dbase.get_environment_by_backend_id(single.name)
                if env is not None:
                    obj = await self.dbase.get_daas_object(env.id_object)
            resp = await self.create_daas_response(
                single, obj, self.config.known_daas_containers
            )
            if await self.check_filter(resp, only_daas, only_user):
                result.append(asdict(resp))
        return result

    async def create_daas_response(
        self,
        single: (
            SystemInfoDockerContainer | SystemInfoDockerImage | SystemInfoProxmoxMachine
        ),
        obj: Optional[DaasObject],
        known_list: list,
    ) -> DaaSObjectResponse:
        """Creates new DaaS response for objects"""
        daas_object = False
        daas_id = single.id_object
        daas_name = single.name
        daas_owner = -1
        daas_type = "none"
        if isinstance(single, SystemInfoProxmoxMachine):
            daas_type = "vm"
        if isinstance(single, SystemInfoDockerImage):
            daas_type = "docker-image"
        if isinstance(single, SystemInfoDockerContainer):
            daas_type = "docker-container"
        if obj is not None:
            daas_id = obj.id
            daas_name = obj.id_user
            daas_owner = obj.id_owner
            daas_object = True
        if single.name in known_list:
            daas_id = single.id_object
            daas_name = single.name
            daas_owner = self.config.system_object_owner
            daas_object = True
        return DaaSObjectResponse(
            daas_id, daas_type, daas_owner, daas_name, daas_object
        )

    async def check_filter(
        self,
        response: DaaSObjectResponse,
        only_daas: bool = False,
        only_user: int = -1,
    ):
        """Check if filter applies"""
        result = False
        if only_daas and response.daas_object is True:
            if only_user != -1 and only_user in (0, response.daas_owner):
                result = True
            elif only_user == -1:
                result = True
        else:
            if only_daas != -1 and only_user in (0, response.daas_owner):
                result = True
            elif only_user == -1:
                result = True
        return result

    # async def synchronize_database_objects_proxmox(self, strategy: PersistanceStrategy):
    #     """Synchronizes database with system wide vms"""
    #     pass
    #
    # async def synchronize_system_objects_proxmox(self, strategy: PersistanceStrategy):
    #     """Synchronizes system with database vms"""
    #     pass
    #
    # async def synchronize_database_objects_docker(self, strategy: PersistanceStrategy):
    #     """Synchronizes database with system wide containers"""
    #     pass
    #
    # async def synchronize_system_objects_docker(self, strategy: PersistanceStrategy):
    #     """Synchronizes system with database containers"""
    #     pass
