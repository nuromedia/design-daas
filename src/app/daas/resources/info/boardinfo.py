"""
Dashboard information
"""

from datetime import datetime

from dataclasses import asdict, dataclass
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import (
    Application,
    DaasObject,
    File,
    GuacamoleConnection,
    Instance,
)
from app.daas.db.database import Database
from app.daas.objects.object_instance import InstanceObject
from app.daas.resources.info.objectinfo import Objectinfo
from app.daas.resources.limits.ressource_limits import RessourceLimits
from app.qweb.common.qweb_tools import get_backend_component
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class DashboardFileObject:
    """DashboardObject FileObject"""

    id: str
    id_owner: int
    name: str
    version: str
    os_type: str
    localpath: str
    remotepath: str
    filesize: int
    created_at: datetime


@dataclass
class DashboardConnectionObject:
    """DashboardObject ConnectionObject"""

    id_inst: str
    viewer_url: str
    current_protocol: str
    viewer_resolution: str
    viewer_resize: str
    viewer_scale: str
    viewer_dpi: int
    viewer_colors: int
    viewer_force_lossless: bool


@dataclass
class DashboardApplicationObject:
    """DashboardObject ApplicationObject"""

    id_app: str
    id_owner: int
    id_file: Optional[str]
    id_template: Optional[str]
    os_type: str
    object_type: str
    name: str
    version: str
    installer_type: str = ""


@dataclass
class DashboardInstanceObject:
    """DashboardObject InstanceObject"""

    id_instance: str
    id_object: str
    id_owner: int
    id_con: Optional[str]
    name: str
    name_env: str
    os_type: str
    object_type: str
    object_state: str
    created_at: datetime
    booted_at: datetime
    connected_at: datetime


@dataclass
class DashboardEnvironmentObject:
    """DashboardObject EnvironmentObject"""

    id_env: str
    id_object: str
    id_owner: int
    name: str
    name_object: str
    os_type: str
    object_state: str
    env_apps: dict
    env_tasks: dict
    env_target: dict
    created_at: str


@dataclass
class DashboardUserObject:
    """DashboardObject UserObject"""

    id_object: str
    id_owner: int
    id_user: str
    id_owner: int
    os_type: str
    object_type: str
    object_state: str
    object_mode: str
    object_mode_extended: str
    object_state: str


@dataclass
class DashboardInfo:
    """Dashboard Info"""

    available_objects: list[dict]
    available_environments: list[dict]
    available_instances: list[dict]
    available_applications: list[dict]
    available_files: list[dict]
    available_connections: list[dict]
    available_ressources: dict
    utilized_ressources: dict


# pylint: disable=too-few-public-methods
class DashboardInfoStore(Loggable):
    """Sysinfo object to provide DashboardInfo"""

    def __init__(self):
        Loggable.__init__(self, LogTarget.SYS)
        self.dbase = Database()

    async def initialize(self):
        await self.dbase.connect()
        self._log_info("DashboardInfo initialized")

    # pylint: disable=too-many-locals,import-outside-toplevel
    async def get_dashboard_info(self, userid: int) -> DashboardInfo:
        """Dashboard info"""
        limits = await get_backend_component(BackendName.LIMITS, RessourceLimits)

        # Object list
        user_objects: list[DaasObject] = await self.dbase.get_daas_objects_available(
            userid
        )
        objlist = [
            DashboardUserObject(
                x.id,
                x.id_owner,
                x.id_user,
                x.os_type,
                x.object_type,
                x.object_state,
                x.object_mode,
                x.object_mode_extended,
            )
            for x in user_objects
        ]

        envlist: list[DashboardEnvironmentObject] = []
        for obj in user_objects:
            envs = await self.dbase.get_environments_by_object(obj.id)
            for env in envs:
                # obj = await dbase.get_daas_object(env.id_object)
                if obj is not None:

                    apps = {}
                    for app in env.env_apps:
                        name = app["name"]
                        apps[name] = app
                    tasks = {}
                    for task in env.env_tasks:
                        name = task["cmd"]
                        tasks[name] = task

                    envlist.append(
                        DashboardEnvironmentObject(
                            env.id,
                            env.id_object,
                            obj.id_owner,
                            env.name,
                            obj.id_user,
                            obj.os_type,
                            env.state,
                            apps,
                            tasks,
                            env.env_target,
                            f"{env.created_at}",
                        )
                    )

        # Files
        all_files: list[File] = await self.dbase.get_all_files(userid)
        filelist = [
            DashboardFileObject(
                file.id,
                file.id_owner,
                file.name,
                file.version,
                file.os_type,
                file.localpath,
                file.remotepath,
                file.filesize,
                file.created_at,
            )
            for file in all_files
        ]
        # Apps
        all_apps: list[Application] = await self.dbase.get_all_applications(userid)
        applist = [
            DashboardApplicationObject(
                app.id,
                app.id_owner,
                app.id_file,
                app.id_template,
                app.os_type,
                "vm" if app.os_type in ("win10", "win11", "l26vm") else "container",
                app.name,
                app.version,
                app.installer_type,
            )
            for app in all_apps
        ]

        # Instance List
        all_insts: list[InstanceObject] = await self.dbase.get_instances_by_owner(
            userid
        )
        instlist: list[DashboardInstanceObject] = []
        for inst in all_insts:
            if inst.app.id_owner in (0, userid):
                envname = ""
                if inst.env is not None:
                    envname = inst.env.name
                instlist.append(
                    DashboardInstanceObject(
                        inst.id,
                        inst.app.id,
                        inst.app.id_owner,
                        inst.id_con,
                        inst.app.id_user,
                        envname,
                        inst.app.os_type,
                        inst.app.object_type,
                        inst.app.object_state,
                        inst.created_at,
                        inst.booted_at,
                        inst.connected_at,
                    )
                )

        # Connections
        conlist = []
        for inst_info in instlist:
            if inst_info.id_con is not None:
                con = await self.dbase.get_guacamole_connection(inst_info.id_con)
                if con is not None and isinstance(con, GuacamoleConnection):
                    inst = await self.dbase.get_instance_by_id(inst_info.id_instance)
                    if inst is not None and isinstance(inst, Instance):
                        conlist.append(
                            DashboardConnectionObject(
                                inst.id,
                                con.viewer_url,
                                con.protocol,
                                inst.app.viewer_resolution,
                                inst.app.viewer_resize,
                                inst.app.viewer_scale,
                                inst.app.viewer_dpi,
                                inst.app.viewer_colors,
                                inst.app.viewer_force_lossless,
                            )
                        )

        infotool = Objectinfo()
        await infotool.initialize()
        utilized = await infotool.get_objectinfo_user(userid)
        limit = await limits.get_user_limit(userid)
        dict_limit = {}
        if limit is not None:
            dict_limit = asdict(limit)
        # Create info
        info = DashboardInfo(
            [asdict(x) for x in objlist],
            [asdict(x) for x in envlist],
            [asdict(x) for x in instlist],
            [asdict(x) for x in applist],
            [asdict(x) for x in filelist],
            [asdict(x) for x in conlist],
            dict_limit,
            asdict(utilized),
        )
        return info
