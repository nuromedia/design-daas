"""Container Tasks"""

from dataclasses import asdict
from enum import Enum
from app.daas.common.enums import BackendName
from app.daas.container.docker.DockerRequest import DockerRequest
from app.daas.objects.object_instance import InstanceObject
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.objects.object_container import (
    ContainerObject,
    get_empty_container_object,
)
from app.daas.common.ctx import (
    create_response_url_start,
    create_response_url_stop,
    get_backend_component,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)


class ContainerTask(Enum):
    """Node processor tasktype"""

    CONT_DAEMON_INFO = "CONT_DAEMON_INFO"
    CONT_IMAGE_INSPECT = "CONT_IMAGE_INSPECT"
    CONT_IMAGE_BUILD = "CONT_IMAGE_BUILD"
    CONT_IMAGE_DELETE = "CONT_IMAGE_DELETE"
    CONT_IMAGE_LIST = "CONT_IMAGE_LIST"
    CONT_START = "CONT_START"
    CONT_STOP = "CONT_STOP"
    CONT_LIST = "CONT_LIST"
    CONT_LOG = "CONT_LOG"
    CONT_IMAGE_CREATE = "CONT_IMAGE_CREATE"
    CONT_IMAGE_CREATE_ROOT = "CONT_IMAGE_CREATE_ROOT"
    CONT_IMAGE_CLONE = "CONT_IMAGE_CLONE"


async def image_create(args: TaskArgs) -> QwebResult:
    """Creates new container object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", ContainerObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        entity = await get_empty_container_object(args.user.id_user, **reqargs)
        return await entity.baseimage_create(reqargs)
    return QwebResult(400, {}, 1, "object already exists")


async def image_create_root(args: TaskArgs) -> QwebResult:
    """Creates new container object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", ContainerObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        entity = await get_empty_container_object(args.user.id_user, **reqargs)
        return await entity.baseimage_create(reqargs)
    return QwebResult(400, {}, 1, "object already exists")


async def image_clone(args: TaskArgs) -> QwebResult:
    """Clones into new container object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    old = get_request_object(args.ctx, "old", ContainerObject)
    entity = get_request_object_optional(args.ctx, "new", ContainerObject)
    reqargs = args.req.request_context.request_args.copy()
    reqargs["id_owner"] = args.user.id_user
    if entity is None:
        if old is not None:
            reqargs["cores"] = old.hw_cpus
            reqargs["memsize"] = old.hw_memory
            reqargs["disksize"] = old.hw_disksize
            entity = await get_empty_container_object(args.user.id_user, **reqargs)
            return await entity.baseimage_clone(reqargs["id"], reqargs)
        return QwebResult(400, {}, 1, "No object to clone from")
    return QwebResult(400, {}, 1, "object already exists")


async def image_build(args: TaskArgs) -> QwebResult:
    """Builds specified docker image"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ContainerObject)
    return await entity.image_build()


async def image_delete(args: TaskArgs) -> QwebResult:
    """Deletes specified docker image"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ContainerObject)
    return await entity.image_delete()


async def image_list(args: TaskArgs) -> QwebResult:
    """Lists docker image"""
    # TODO: Add detailed sorting for users and daas objects
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    api = get_backend_component(args.ctx, BackendName.CONTAINER.value, DockerRequest)
    reqargs = args.req.request_context.request_args.copy()
    detailed = True if "detailed" in reqargs else False
    infolist = await api.docker_image_list(detailed)
    dictlist = [asdict(x) for x in infolist]
    return QwebResult(200, dictlist)


async def container_start(args: TaskArgs) -> QwebResult:
    """Starts specified image as container"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ContainerObject)
    reqargs = args.req.request_context.request_args
    connect = "connect" in reqargs
    inst = await entity.start(args.user.id_user, connect, "run-debug")
    if inst is not None:
        return await create_response_url_start(connect, inst.id)
    return QwebResult(400, {}, 1, "No instance")


async def container_stop(args: TaskArgs) -> QwebResult:
    """Stops specified image as container"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", InstanceObject)
    if isinstance(entity.app, ContainerObject):
        stopped = await entity.app.stop(entity, True)
        return await create_response_url_stop(stopped)
    return QwebResult(400, {}, 1, "Invalid instance type")


async def container_list(args: TaskArgs) -> QwebResult:
    """Lists containers"""
    # TODO: Add detailed sorting for users and daas objects
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    api = get_backend_component(args.ctx, BackendName.CONTAINER.value, DockerRequest)
    reqargs = args.req.request_context.request_args.copy()
    detailed = True if "detailed" in reqargs else False
    infolist = await api.docker_container_list(detailed)
    dictlist = [asdict(x) for x in infolist]
    return QwebResult(200, dictlist)


async def container_logs(args: TaskArgs) -> QwebResult:
    """Returns container logs"""
    # TODO: Add detailed sorting for users and daas objects
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    api = get_backend_component(args.ctx, BackendName.CONTAINER.value, DockerRequest)
    entity = get_request_object(args.ctx, "entity", ContainerObject)
    tag = await entity.get_container_tag()
    code, info, err = await api.docker_container_logs(tag)
    if code == 0:
        return QwebResult(200, {}, 0, info)
    return QwebResult(400, {}, code, f"{info}{err}")


async def image_inspect(args: TaskArgs) -> QwebResult:
    """Retrieves info from specified docker image"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", ContainerObject)
    return await entity.status_container()


async def daemon_info(args: TaskArgs) -> QwebResult:
    """Retrieves info from utilized docker daemon"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    api = get_backend_component(args.ctx, BackendName.CONTAINER.value, DockerRequest)
    data = await api.docker_get_daemoninfo()
    return QwebResult(200, data)
