"""Info Tasks"""

from enum import Enum
from app.daas.common.model import Application, DaasObject
from app.daas.objects.object_application import ApplicationObject
from app.daas.objects.object_container import ContainerObject
from app.daas.objects.object_machine import MachineObject
from app.daas.resources.info.monitoring import MonitoringInfo, MonitoringInfoTool
from app.qweb.common.common import TaskArgs
from app.qweb.common.enums import ScheduledTaskFilter
from app.qweb.common.qweb_tools import get_service
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import get_request_object_optional, log_task_arguments
from app.qweb.service.service_context import ServiceComponent
from app.qweb.service.service_tasks import QwebTaskManager


class AdminTask(Enum):
    """Info tasktype"""

    ADMIN_DASHBOARD = "ADMIN_DASHBOARD"
    ADMIN_MONITORING = "ADMIN_MONITORING"
    ADMIN_MONITORING_TASKS = "ADMIN_MONITORING_TASKS"
    ADMIN_MONITORING_APPS = "ADMIN_MONITORING_APPS"
    ADMIN_MONITORING_FILES = "ADMIN_MONITORING_FILES"
    ADMIN_MONITORING_SOCKETS = "ADMIN_MONITORING_SOCKETS"
    ADMIN_MONITORING_HOST = "ADMIN_MONITORING_HOST"
    ADMIN_MONITORING_OBJECTS = "ADMIN_MONITORING_OBEJCTS"
    ADMIN_MONITORING_UTILIZATION = "ADMIN_MONITORING_UTILIZATION"
    ADMIN_MONITORING_LIMITS = "ADMIN_MONITORING_LIMITS"
    ADMIN_ASSIGN_OBJ_TO_USER = "ADMIN_ASSIGN_OBJ_TO_USER"
    ADMIN_ASSIGN_APP = "ADMIN_ASSIGN_APP"
    ADMIN_TASK_LIST = "ADMIN_TASK_LIST"
    ADMIN_TASK_STOP = "ADMIN_TASK_STOP"


async def admin_monitoring_info(args: TaskArgs) -> QwebResult:
    """Returns monitoring info object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    userid = args.user.id_user
    mon = MonitoringInfoTool()
    detailed = False
    include_hostinfo = False
    taskinfo = await mon.create_monitoring_info_tasks(userid)
    fileinfo = await mon.create_monitoring_info_files(userid)
    appinfo = await mon.create_monitoring_info_apps(userid)
    socketinfo = await mon.create_monitoring_info_websockets(userid)
    hostinfo = await mon.create_monitoring_info_host(include_hostinfo)
    objinfo = await mon.create_monitoring_info_objects(detailed, userid)
    objutil = await mon.create_monitoring_info_utilization(userid)
    limitinfo = await mon.create_monitoring_info_limit(userid)
    info_all = MonitoringInfo(
        taskinfo, fileinfo, appinfo, hostinfo, socketinfo, objinfo, objutil, limitinfo
    )
    return QwebResult(200, info_all.tojson())


async def admin_monitoring_info_tasks(args: TaskArgs) -> QwebResult:
    """Returns monitoring info tasks"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_tasks(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_apps(args: TaskArgs) -> QwebResult:
    """Returns app infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_apps(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_files(args: TaskArgs) -> QwebResult:
    """Returns file infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_files(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_sockets(args: TaskArgs) -> QwebResult:
    """Returns socket infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_websockets(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_host(args: TaskArgs) -> QwebResult:
    """Returns host infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    include_hostinfo = True
    mon = MonitoringInfoTool()
    taskinfo = await mon.create_monitoring_info_host(include_hostinfo)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_objects(args: TaskArgs) -> QwebResult:
    """Returns object infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_objects(False, userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_utilization(args: TaskArgs) -> QwebResult:
    """Returns utilization infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_utilization(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_monitoring_info_limits(args: TaskArgs) -> QwebResult:
    """Returns resource limit infos"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mon = MonitoringInfoTool()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if "id_owner" in reqargs:
        userid = reqargs["id_owner"]
    taskinfo = await mon.create_monitoring_info_limit(userid)
    return QwebResult(200, taskinfo.tojson())


async def admin_assign_obj_to_user(args: TaskArgs) -> QwebResult:
    """Assigns obj to user"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", DaasObject)
    reqargs = args.req.request_context.request_args
    userid = reqargs["owner"]
    if entity is not None:
        if isinstance(entity, MachineObject | ContainerObject):
            changed = await entity.change_owner(userid)
            if changed:
                return QwebResult(200, {})
            return QwebResult(400, {}, 1, "Could not change ownership")
        return QwebResult(400, {}, 2, "Invalid object type")
    return QwebResult(400, {}, 3, "No object")


async def admin_assign_app(args: TaskArgs) -> QwebResult:
    """Assigns app to user"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    reqargs = args.req.request_context.request_args
    userid = reqargs["owner"]
    if entity is not None:
        if isinstance(entity, ApplicationObject):
            changed = await entity.change_owner(userid)
            if changed:
                return QwebResult(200, {})
            return QwebResult(400, {}, 1, "Could not change ownership")
        return QwebResult(400, {}, 2, "Invalid app type")
    return QwebResult(400, {}, 3, "No app")


async def admin_tasklist(args: TaskArgs) -> QwebResult:
    """Returns task list"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    reqargs = args.req.request_context.request_args
    dicts = await _get_filtered_tasks(reqargs)
    return QwebResult(200, dicts)


async def admin_task_stop(args: TaskArgs) -> QwebResult:
    """Stops task"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    mancomp: QwebTaskManager = await get_service(ServiceComponent.TASK, QwebTaskManager)
    reqargs = args.req.request_context.request_args
    dicts = await _get_filtered_tasks(reqargs)
    for x in dicts:
        stopped = await mancomp.stop_scheduled_task(x["id_task"])
        if stopped is False:
            return QwebResult(400, {}, 1, "Error on stopping task")
    return QwebResult(200, {})


async def _get_filtered_tasks(reqargs: dict) -> list[dict]:

    userid = 0
    if reqargs["id_owner"] != "":
        userid = int(reqargs["id_owner"])
    objid = reqargs["id_object"]
    instid = reqargs["id_instance"]
    flt = ScheduledTaskFilter.ALL
    if "state" in reqargs:
        if reqargs["state"] == ScheduledTaskFilter.RUNNING.value:
            flt = ScheduledTaskFilter.RUNNING
        elif reqargs["state"] == ScheduledTaskFilter.FINAL.value:
            flt = ScheduledTaskFilter.FINAL
    mancomp: QwebTaskManager = await get_service(ServiceComponent.TASK, QwebTaskManager)
    tasks = await mancomp.get_scheduled_tasks(flt)
    filtered = await mancomp.filter_tasks(tasks, userid, objid, instid)
    return [v.to_json() for _, v in filtered.items()]
