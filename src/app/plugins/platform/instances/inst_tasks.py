"""Instance Tasks"""

from enum import Enum
from app.daas.common.enums import BackendName
from app.daas.objects.object_instance import InstanceObject
from app.daas.storage.filestore import Filestore
from app.qweb.common.common import TaskArgs
from app.qweb.common.qweb_tools import get_database
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import (
    get_backend_component,
    get_request_object,
    log_task_arguments,
)


class InstanceTask(Enum):
    """Instance tasktype"""

    INST_VMINVOKE_APP = "INST_VMINVOKE_APP"
    INST_VMINVOKE_CMD = "INST_VMINVOKE_CMD"
    INST_VMINVOKE_SSH = "INST_VMINVOKE_SSH"
    INST_VMINVOKE_ACTION = "INST_VMINVOKE_ACTION"
    INST_VMINVOKE_RESOLUTION = "INST_VMINVOKE_RESOLUTION"
    INST_VMINVOKE_OSPACKAGE = "INST_VMINVOKE_OSPACKAGE"
    INST_VMINVOKE_UPLOAD = "INST_VMINVOKE_UPLOAD"
    INST_VMINVOKE_FILESYSTEM = "INST_VMINVOKE_FILESYSTEM"
    INST_VMINVOKE_LIST = "INST_VMINVOKE_LIST"
    INST_VMINVOKE_TEST_ICMP = "INST_VMINVOKE_TEST_ICMP"
    INST_VMINVOKE_TEST_SSH = "INST_VMINVOKE_TEST_SSH"
    INST_VMINVOKE_RTT = "INST_VMINVOKE_RTT"


async def vminvoke_app(args: TaskArgs) -> QwebResult:
    """Invokes app command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_app(reqargs["cmd"], reqargs["args"])


async def vminvoke_cmd(args: TaskArgs) -> QwebResult:
    """Invokes command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_cmd(reqargs["cmd"], reqargs["args"])


async def vminvoke_ssh(args: TaskArgs) -> QwebResult:
    """Invokes ssh command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_ssh(reqargs["cmd"], reqargs["args"])


async def vminvoke_action(args: TaskArgs) -> QwebResult:
    """Invokes action command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_action(reqargs["cmd"], reqargs["args"])


async def vminvoke_resolution(args: TaskArgs) -> QwebResult:
    """Invokes resolution command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_resolution(reqargs["cmd"], reqargs["args"])


async def vminvoke_ospackage(args: TaskArgs) -> QwebResult:
    """Invokes ospackage command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_ospackage(reqargs["cmd"], reqargs["args"])


async def vminvoke_upload(args: TaskArgs) -> QwebResult:
    """Invokes upload command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    absfile = await _upload_tmpfile(args)
    reqargs = args.req.request_context.request_args
    run = reqargs["execute"] != ""
    win = await entity.needs_pstools()
    return await entity.inst_vminvoke_upload(absfile, win, run)


async def vminvoke_filesystem(args: TaskArgs) -> QwebResult:
    """Invokes filesystem command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    code, str_out, str_err = await entity.inst_vminvoke_filesystem(
        reqargs["cmd"], reqargs["args"]
    )
    if code == 0:
        return QwebResult(200, {}, 0, f"{str_out}{str_err}")
    return QwebResult(400, {}, 1, "Error on invoke_upload()")


async def vminvoke_list(args: TaskArgs) -> QwebResult:
    """Invokes list command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", list)
    return QwebResult(200, await _enumerate_instances(entity))


async def vminvoke_test_icmp(args: TaskArgs) -> QwebResult:
    """Invokes icmp test command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_test_icmp()


async def vminvoke_test_ssh(args: TaskArgs) -> QwebResult:
    """Invokes ssh test command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_test_ssh()


async def vminvoke_rtt(args: TaskArgs) -> QwebResult:
    """Invokes ssh test command"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    reqargs = args.req.request_context.request_args
    return await entity.inst_vminvoke_rtt(reqargs["cmd"], reqargs["args"])


async def _upload_tmpfile(args: TaskArgs) -> str:
    reqargs = args.req.request_context.request_args
    file = reqargs["file"]
    name = file.filename
    userid = args.user.id_user
    store = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    await store.upload_user_file_tmp(reqargs["file"], name, userid)
    return await store.get_user_file_tmp(name, userid)


async def _enumerate_instances(instances: list) -> list[dict]:
    return [
        await inst.get_connection_info()
        for inst in instances
        if isinstance(inst, InstanceObject)
    ]
