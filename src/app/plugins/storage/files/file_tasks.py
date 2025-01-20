"""File Tasks"""

from datetime import datetime
from enum import Enum
from app.daas.common.enums import BackendName
from app.daas.common.model import Application, File
from app.daas.db.database import Database
from app.daas.storage.filestore import Filestore
from app.qweb.common.common import TaskArgs
from app.qweb.processing.processor import QwebResult
from app.daas.common.ctx import (
    get_backend_component,
    get_request_object,
    get_request_object_optional,
    log_task_arguments,
)


class FileTask(Enum):
    """File tasktype"""

    FILE_GET = "FILE_GET"
    FILE_DELETE = "FILE_DELETE"
    FILE_DELETE_SHARED = "FILE_DELETE_SHARED"
    FILE_LIST = "FILE_LIST"
    FILE_CREATE = "FILE_CREATE"
    FILE_UPDATE = "FILE_UPDATE"
    FILE_CREATE_SHARED = "FILE_CREATE_SHARED"
    FILE_UPDATE_SHARED = "FILE_UPDATE_SHARED"

    APP_GET = "APP_GET"
    APP_DELETE = "APP_DELETE"
    APP_DELETE_SHARED = "APP_DELETE_SHARED"
    APP_LIST = "APP_LIST"
    APP_CREATE = "APP_CREATE"
    APP_UPDATE = "APP_UPDATE"
    APP_CREATE_SHARED = "APP_CREATE_SHARED"
    APP_UPDATE_SHARED = "APP_UPDATE_SHARED"


async def files_create(args: TaskArgs) -> QwebResult:
    """Creates file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", File)
    if entity is not None:
        return QwebResult(400, {}, 1, "File exists")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    name = f"{reqargs['id']}.file"
    userid = args.user.id_user
    reqpath = reqargs["filepath"]
    stored = await api.upload_user_file_upload(reqargs["file"], name, userid)
    if stored:
        filepath = await api.get_user_file_upload(name, userid)
        filesize = await api.get_filesize(filepath)
        if filepath != "":
            file = await _make_file(userid, filepath, reqpath, filesize, reqargs)
            await dbase.create_file(file)
            return QwebResult(200, {})
    return QwebResult(500, {}, 2, "File exists")


async def files_create_shared(args: TaskArgs) -> QwebResult:
    """Creates shared file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", File)
    if entity is not None:
        return QwebResult(400, {}, 1, "File exists")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    name = f"{reqargs['id']}.file"
    userid = 0
    reqpath = reqargs["filepath"]
    stored = await api.upload_user_file_shared(reqargs["file"], name, userid)
    if stored:
        filepath = await api.get_user_file_shared(name, userid)
        filesize = await api.get_filesize(filepath)
        if filepath != "":
            file = await _make_file(userid, filepath, reqpath, filesize, reqargs)
            await dbase.create_file(file)
            return QwebResult(200, {})
    return QwebResult(500, {}, 2, "File exists")


async def files_update(args: TaskArgs) -> QwebResult:
    """Updates file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", File)
    if entity is None:
        return QwebResult(400, {}, 1, "No file")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    name = f"{reqargs['id']}.file"
    userid = args.user.id_user
    reqpath = reqargs["filepath"]
    stored = await api.upload_user_file_upload(reqargs["file"], name, userid)
    if stored:
        filepath = await api.get_user_file_upload(name, userid)
        filesize = await api.get_filesize(filepath)
        if filepath != "":
            file = await _make_file(userid, filepath, reqpath, filesize, reqargs)
            await dbase.create_file(file)
            return QwebResult(200, {})
    return QwebResult(500, {}, 2, "File exists")


async def files_update_shared(args: TaskArgs) -> QwebResult:
    """Updates shared file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object(args.ctx, "entity", File)
    if entity is None:
        return QwebResult(400, {}, 1, "No file")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    name = f"{reqargs['id']}.file"
    userid = 0
    reqpath = reqargs["filepath"]
    stored = await api.upload_user_file_shared(reqargs["file"], name, userid)
    if stored:
        filepath = await api.get_user_file_shared(name, userid)
        filesize = await api.get_filesize(filepath)
        if filepath != "":
            file = await _make_file(userid, filepath, reqpath, filesize, reqargs)
            await dbase.create_file(file)
            return QwebResult(200, {})
    return QwebResult(500, {}, 2, "File exists")


async def files_get(args: TaskArgs) -> QwebResult:
    """Retrieves file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", File)
    if entity is not None:
        return QwebResult(200, entity.get_data())
    return QwebResult(400, {}, 1, "No file")


async def files_list(args: TaskArgs) -> QwebResult:
    """Lists file objects"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    dbase = await _get_dbase()
    userid = args.user.id_user
    reqargs = args.req.request_context.request_args
    choice = reqargs["choice"]
    assert userid != -1
    if choice == "user":
        filelist = await dbase.get_user_files(userid)
    elif choice == "shared":
        filelist = await dbase.get_shared_files()
    else:
        filelist = await dbase.get_all_files(userid)
    return QwebResult(200, filelist)


async def files_delete(args: TaskArgs) -> QwebResult:
    """Deletes file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", File)
    if entity is None:
        return QwebResult(400, {}, 1, "No file")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    store_delete = await api.delete_user_file_upload(entity.id, entity.id_owner)
    db_delete = await dbase.delete_file(entity.id)
    if store_delete and db_delete:
        return QwebResult(200, {})
    msg = f"File not properly deleted: {store_delete},{db_delete}"
    return QwebResult(400, {}, 1, msg)


async def files_delete_shared(args: TaskArgs) -> QwebResult:
    """Deletes shared file object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", File)
    if entity is None:
        return QwebResult(400, {}, 1, "No file")
    api = get_backend_component(args.ctx, BackendName.FILE.value, Filestore)
    dbase = await _get_dbase()
    store_delete = await api.delete_user_file_shared(entity.id, 0)
    db_delete = await dbase.delete_file(entity.id)
    if store_delete and db_delete:
        return QwebResult(200, {})
    msg = f"File not properly deleted: {store_delete},{db_delete}"
    return QwebResult(400, {}, 1, msg)


async def app_create(args: TaskArgs) -> QwebResult:
    """Creates app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if entity is None:
        app = await _make_app(userid, reqargs)
        await dbase.create_application(app)
        return QwebResult(200, {})
    return QwebResult(500, {}, 2, "App exists")


async def app_create_shared(args: TaskArgs) -> QwebResult:
    """Creates shared app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    userid = 0
    if entity is None:
        app = await _make_app(userid, reqargs)
        await dbase.create_application(app)
        return QwebResult(200, {})
    return QwebResult(500, {}, 2, "App exists")


async def app_update(args: TaskArgs) -> QwebResult:
    """Updates app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    userid = args.user.id_user
    if entity is not None:
        app = await _make_app(userid, reqargs)
        await dbase.update_application(app)
        return QwebResult(200, {})
    return QwebResult(500, {}, 2, "No app")


async def app_update_shared(args: TaskArgs) -> QwebResult:
    """Updates shared app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    dbase = await _get_dbase()
    reqargs = args.req.request_context.request_args
    userid = 0
    if entity is not None:
        app = await _make_app(userid, reqargs)
        await dbase.update_application(app)
        return QwebResult(200, {})
    return QwebResult(500, {}, 2, "No app")


async def app_get(args: TaskArgs) -> QwebResult:
    """Retrieves app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    if entity is not None:
        return QwebResult(200, entity.get_data())
    return QwebResult(400, {}, 1, "No app")


async def app_list(args: TaskArgs) -> QwebResult:
    """Lists app objects"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    dbase = await _get_dbase()
    userid = args.user.id_user
    reqargs = args.req.request_context.request_args
    choice = reqargs["choice"]
    assert userid != -1
    if choice == "user":
        filelist = await dbase.get_user_applications(userid)
    elif choice == "shared":
        filelist = await dbase.get_shared_applications()
    else:
        filelist = await dbase.get_all_applications(userid)
    return QwebResult(200, filelist)


async def app_delete(args: TaskArgs) -> QwebResult:
    """Deletes app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    if entity is None:
        return QwebResult(400, {}, 1, "No app")
    dbase = await _get_dbase()
    db_delete = await dbase.delete_application(entity.id)
    if db_delete:
        return QwebResult(200, {})
    msg = f"File not properly deleted: {db_delete}"
    return QwebResult(400, {}, 1, msg)


async def app_delete_shared(args: TaskArgs) -> QwebResult:
    """Deletes shared app object"""
    log_task_arguments(args.ctx, args.req, args.info, args.user)
    entity = get_request_object_optional(args.ctx, "entity", Application)
    if entity is None:
        return QwebResult(400, {}, 1, "No app")
    dbase = await _get_dbase()
    db_delete = await dbase.delete_application(entity.id)
    if db_delete:
        return QwebResult(200, {})
    msg = f"File not properly deleted: {db_delete}"
    return QwebResult(400, {}, 1, msg)


async def _make_file(
    userid: int, localpath: str, remotepath: str, filesize: int, args: dict
):
    return File(
        args["id"],
        userid,
        args["filename"],
        args["version"],
        args["os_type"],
        localpath,
        remotepath,
        filesize,
        datetime.now(),
    )


async def _make_app(userid: int, args: dict):
    return Application(
        args["id"],
        userid,
        args["name"],
        args["version"],
        args["id_file"],
        args["id_template"],
        args["os_type"],
        args["installer"],
        args["installer_args"],
        args["installer_type"],
        args["target"],
        args["target_args"],
        datetime.now(),
    )


async def _get_dbase() -> Database:
    dbase = Database()
    await dbase.connect()
    assert dbase.connected is True
    return dbase
