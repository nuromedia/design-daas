"""
Monitoring information
"""

from dataclasses import asdict, dataclass
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import RessourceInfo
from app.daas.proxy.proxy_registry import ProxyRegistry
from app.daas.resources.info.infotools import create_taskinfo_result
from app.daas.resources.info.objectinfo import Objectinfo
from app.daas.resources.info.hostinfo import HostRessources
from app.daas.resources.info.sysinfo import Systeminfo
from app.daas.resources.limits.ressource_limits import RessourceLimits
from app.qweb.common.enums import ScheduledTaskFilter
from app.qweb.common.qweb_tools import get_backend_component, get_database, get_service
from app.qweb.service.service_context import ServiceComponent
from app.qweb.service.service_tasks import QwebTaskManager


@dataclass
class MonitoringInfoTasks:
    """InfoObject for Monitoring tasks"""

    tasks_list: list
    tasks_running: int
    tasks_finalized: int

    def tojson(self):
        """Converts object to json"""
        return {
            "all": self.tasks_list,
            "tasks_running": self.tasks_running,
            "tasks_finalized": self.tasks_finalized,
        }


@dataclass
class MonitoringInfoFiles:
    """InfoObject for Monitoring files"""

    files_list: list
    files_user: int
    files_shared: int
    size_all: int
    size_user: int
    size_shared: int

    def tojson(self):
        """Converts object to json"""
        return {
            "all": self.files_list,
            "files_user": self.files_user,
            "files_shared": self.files_shared,
            "size_all": self.size_all,
            "size_user": self.size_user,
            "size_shared": self.size_shared,
        }


@dataclass
class MonitoringInfoApps:
    """InfoObject for Monitoring apps"""

    app_list: list
    apps_user: int
    apps_shared: int

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfoWebsockets:
    """InfoObject for Monitoring websockets"""

    active_websockets: dict[str, dict]
    closed_websockets: dict[str, dict]

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfoHost:
    """InfoObject for Monitoring host ressources"""

    available_cpus: int
    available_memory: int
    available_disk_local: int
    available_disk_ceph: int
    available_disk_iso: int
    available_disk_images: int
    inuse_cpus: float
    inuse_memory: int
    inuse_disk_local: int
    inuse_disk_ceph: int
    inuse_disk_iso: int
    inuse_disk_images: int

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfoObjects:
    """InfoObject for Monitoring DaaSObjects"""

    vms_usage_online: dict
    vms_usage_offline: dict
    vms_usage_total: dict
    container_usage_online: dict
    container_usage_offline: dict
    container_usage_total: dict
    both_usage_online: dict
    both_usage_offline: dict
    both_usage_total: dict

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfoUtilization:
    """InfoObject for Utilization DaaSObjects"""

    objects: int
    instances: int
    object_vms: int
    object_images: int
    instance_vms: int
    instance_images: int
    max_cpus: int
    max_memory: int
    max_diskspace: int
    utilized_cpus: int
    utilized_memory: int
    utilized_diskspace: int

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfoLimit:
    """InfoObject for Utilization DaaSObjects"""

    limits: list[RessourceInfo]
    syslimit: Optional[RessourceInfo]
    fallback: Optional[RessourceInfo]

    def tojson(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class MonitoringInfo:
    """InfoObject for Monitoring"""

    info_tasks: MonitoringInfoTasks
    info_files: MonitoringInfoFiles
    info_apps: MonitoringInfoApps
    info_host: MonitoringInfoHost
    info_sockets: MonitoringInfoWebsockets
    info_objects: MonitoringInfoObjects
    info_utilization: MonitoringInfoUtilization
    info_limits: MonitoringInfoLimit

    def tojson(self):
        """Converts object to json"""
        return {
            "info_tasks": self.info_tasks.tojson(),
            "info_apps": self.info_apps.tojson(),
            "info_files": self.info_files.tojson(),
            "info_host": self.info_host.tojson(),
            "info_sockets": self.info_sockets.tojson(),
            "info_objects": self.info_objects.tojson(),
            "info_utilization": self.info_utilization.tojson(),
            "info_limits": self.info_limits.tojson(),
        }


class MonitoringInfoTool:
    """Monitoring info"""

    async def create_monitoring_info_host(
        self,
        include_hostinfo: bool = False,
    ) -> MonitoringInfoHost:
        systool = await get_backend_component(BackendName.INFO, Systeminfo)
        if include_hostinfo is False:
            hostinfo = HostRessources(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        else:
            hostinfo = await systool.get_hostinfo()
        assert hostinfo is not None
        return MonitoringInfoHost(
            hostinfo.max_cpus,
            hostinfo.max_memory,
            hostinfo.max_disk_space_data,
            hostinfo.max_disk_space_ceph,
            hostinfo.max_disk_space_iso,
            hostinfo.max_disk_space_images,
            hostinfo.utilized_cpus,
            hostinfo.utilized_memory,
            hostinfo.utilized_disk_space_data,
            hostinfo.utilized_disk_space_ceph,
            hostinfo.utilized_disk_space_iso,
            hostinfo.utilized_disk_space_images,
        )

    async def create_monitoring_info_limit(
        self,
        userid: int = 0,
    ) -> MonitoringInfoLimit:
        limiter = await get_backend_component(BackendName.LIMITS, RessourceLimits)
        if userid == 0:
            limits = await limiter.list_user_limits()
            if limits is None:
                limits = []
        else:
            limit = await limiter.get_user_limit(userid)
            if limit is not None:
                limits = [limit]
            else:
                limits = []
        return MonitoringInfoLimit(limits, limiter.limit_system, limiter.limit_fallback)

    async def create_monitoring_info_utilization(
        self,
        userid: int = 0,
    ) -> MonitoringInfoUtilization:
        infotool = Objectinfo()
        await infotool.initialize()
        info = await infotool.get_objectinfo_user(userid)
        return MonitoringInfoUtilization(**asdict(info))

    async def create_monitoring_info_websockets(
        self,
        userid: int = 0,
    ) -> MonitoringInfoWebsockets:
        reg = await get_backend_component(BackendName.PROXY, ProxyRegistry)
        active = reg.get_active_connections(userid)
        closed = reg.get_closed_connections(userid)
        return MonitoringInfoWebsockets(active, closed)

    async def create_monitoring_info_objects(
        self, daas_only: bool = True, userid: int = 0, detailed: bool = False
    ) -> MonitoringInfoObjects:
        systool = await get_backend_component(BackendName.INFO, Systeminfo)
        objinfo = await systool.get_filtered_objectinfo(detailed, daas_only, userid)

        return MonitoringInfoObjects(
            asdict(objinfo.vms_usage_online),
            asdict(objinfo.vms_usage_offline),
            asdict(objinfo.vms_usage_total),
            asdict(objinfo.images_usage_online),
            asdict(objinfo.images_usage_offline),
            asdict(objinfo.images_usage_total),
            asdict(objinfo.all_usage_online),
            asdict(objinfo.all_usage_offline),
            asdict(objinfo.all_usage_total),
        )

    async def create_monitoring_info_files(
        self, userid: int = 0
    ) -> MonitoringInfoFiles:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if userid == 0:
            allfiles = await dbase.get_all_files(0)
            userfiles = await dbase.get_user_files(userid)
            sharedfiles = await dbase.get_shared_files()
        else:
            allfiles = await dbase.get_all_files(userid)
            userfiles = await dbase.get_user_files(userid)
            sharedfiles = await dbase.get_shared_files()

        usersize = 0
        for file in userfiles:
            usersize += file.filesize
        sharedsize = 0
        for file in sharedfiles:
            sharedsize += file.filesize

        return MonitoringInfoFiles(
            allfiles,
            len(userfiles),
            len(sharedfiles),
            usersize + sharedsize,
            usersize,
            sharedsize,
        )

    async def create_monitoring_info_apps(self, userid: int = 0) -> MonitoringInfoApps:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        if userid == 0:
            allfiles = await dbase.get_all_applications(0)
            userfiles = []
            sharedfiles = await dbase.get_shared_files()
        else:
            allfiles = await dbase.get_all_applications(userid)
            userfiles = await dbase.get_user_applications(userid)
            sharedfiles = []
        return MonitoringInfoApps(allfiles, len(userfiles), len(sharedfiles))

    async def create_monitoring_info_tasks(
        self, userid: int = 0
    ) -> MonitoringInfoTasks:
        """Create taskinfo"""
        taskman = await get_service(ServiceComponent.TASK, QwebTaskManager)

        tasks_running_ret = []
        tasklist_ret = []
        tasks_final_ret = []

        tasks_running = await taskman.get_scheduled_tasks(ScheduledTaskFilter.RUNNING)
        filtered_running = await taskman.filter_tasks(tasks_running, userid, "", "")
        for _, task in filtered_running.items():
            taskinfo = create_taskinfo_result(task).tojson()
            tasklist_ret.append(taskinfo)
            tasks_running_ret.append(taskinfo)

        tasks_final = await taskman.get_scheduled_tasks(ScheduledTaskFilter.FINAL)
        filtered_final = await taskman.filter_tasks(tasks_final, userid, "", "")
        for _, task in filtered_final.items():
            taskinfo = create_taskinfo_result(task).tojson()
            tasklist_ret.append(taskinfo)
            tasks_final_ret.append(taskinfo)

        return MonitoringInfoTasks(
            tasklist_ret, len(tasks_running_ret), len(tasks_final_ret)
        )
