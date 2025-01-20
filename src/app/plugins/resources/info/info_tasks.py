"""Info Tasks"""

from dataclasses import asdict
from enum import Enum
from app.daas.common.enums import BackendName
from app.daas.resources.info.monitoring import MonitoringInfo, MonitoringInfoTool
from app.daas.resources.info.sysinfo import Systeminfo
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import (
    get_backend_component,
    log_task_arguments,
)


class InfoTask(Enum):
    """Info tasktype"""

    INFO_DASHBOARD = "INFO_DASHBOARD"
    INFO_MONITORING = "INFO_MONITORING"
    INFO_MONITORING_TASKS = "INFO_MONITORING_TASKS"
    INFO_MONITORING_APPS = "INFO_MONITORING_APPS"
    INFO_MONITORING_FILES = "INFO_MONITORING_FILES"
    INFO_MONITORING_SOCKETS = "INFO_MONITORING_SOCKETS"
    INFO_MONITORING_HOST = "INFO_MONITORING_HOST"
    INFO_MONITORING_OBJECTS = "INFO_MONITORING_OBEJCTS"
    INFO_MONITORING_UTILIZATION = "INFO_MONITORING_UTILIZATION"
    INFO_MONITORING_LIMITS = "INFO_MONITORING_LIMITS"


async def dashboard_info(args: TaskArgs) -> QwebResult:
    """Returns dashboard info"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    sys = get_backend_component(args.ctx, BackendName.INFO.value, Systeminfo)
    info = await sys.get_dashboard_info(args.user.id_user)
    if info is not None:
        return QwebResult(200, {"dashboardinfo": asdict(info)})
    return QwebResult(400, {}, 1, "Dashbaordinfo was empty")


async def monitoring_info(args: TaskArgs) -> QwebResult:
    """Returns monitoring info object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)

    userid = args.user.id_user
    mon = MonitoringInfoTool()
    include_hostinfo = True
    taskinfo = await mon.create_monitoring_info_tasks(userid)
    fileinfo = await mon.create_monitoring_info_files(userid)
    appinfo = await mon.create_monitoring_info_apps(userid)
    socketinfo = await mon.create_monitoring_info_websockets(userid)
    hostinfo = await mon.create_monitoring_info_host(include_hostinfo)
    objinfo = await mon.create_monitoring_info_objects(True, userid)
    objutil = await mon.create_monitoring_info_utilization(userid)
    limitinfo = await mon.create_monitoring_info_limit(userid)

    info_all = MonitoringInfo(
        taskinfo, fileinfo, appinfo, hostinfo, socketinfo, objinfo, objutil, limitinfo
    )
    return QwebResult(200, info_all.tojson())


async def monitoring_info_tasks(args: TaskArgs) -> QwebResult:
    """Returns monitoring info tasks"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    userid = args.user.id_user
    mon = MonitoringInfoTool()
    taskinfo = await mon.create_monitoring_info_tasks(userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_apps(args: TaskArgs) -> QwebResult:
    """Returns app infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    userid = args.user.id_user
    mon = MonitoringInfoTool()
    taskinfo = await mon.create_monitoring_info_apps(userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_files(args: TaskArgs) -> QwebResult:
    """Returns file infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    userid = args.user.id_user
    mon = MonitoringInfoTool()
    taskinfo = await mon.create_monitoring_info_files(userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_sockets(args: TaskArgs) -> QwebResult:
    """Returns socket infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    userid = args.user.id_user
    mon = MonitoringInfoTool()
    taskinfo = await mon.create_monitoring_info_websockets(userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_host(args: TaskArgs) -> QwebResult:
    """Returns host infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    include_hostinfo = True
    taskinfo = await mon.create_monitoring_info_host(include_hostinfo)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_objects(args: TaskArgs) -> QwebResult:
    """Returns object infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    userid = args.user.id_user
    taskinfo = await mon.create_monitoring_info_objects(True, userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_utilization(args: TaskArgs) -> QwebResult:
    """Returns utilization infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    userid = args.user.id_user
    taskinfo = await mon.create_monitoring_info_utilization(userid)
    return QwebResult(200, taskinfo.tojson())


async def monitoring_info_limits(args: TaskArgs) -> QwebResult:
    """Returns resource limit infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    userid = args.user.id_user
    taskinfo = await mon.create_monitoring_info_limit(userid)
    return QwebResult(200, taskinfo.tojson())
