from typing import Optional, Type, TypeVar

from app.daas.common.enums import BackendName
from app.qweb.service.service_context import ServiceComponent
from app.qweb.service.service_tasks import ScheduledTask


T = TypeVar("T")


async def get_backend_component(name: BackendName, ret_type: Type[T]) -> T:
    from app.qweb.service.service_runtime import get_qweb_runtime

    runtime = get_qweb_runtime()
    backend = runtime.backends.get(name.value)
    if backend is not None and backend.component is not None:
        if isinstance(backend.component, ret_type):
            return backend.component
        hastype = type(backend.component)
        raise TypeError(f"Backend has invalid type: {name} -> {hastype}")
    raise ValueError(f"Backend is None: {backend}")


async def get_backend(name: BackendName, ret_type: Type[T]) -> T:
    from app.qweb.service.service_runtime import get_qweb_runtime

    runtime = get_qweb_runtime()
    backend = runtime.backends.get(name.value)
    if backend is not None:
        if isinstance(backend, ret_type):
            return backend
        hastype = type(backend)
        raise TypeError(f"Backend has invalid type: {name} -> {hastype}")
    raise ValueError(f"Backend is None: {backend}")


async def get_service(component: ServiceComponent, ret_type: Type[T]) -> T:
    from app.qweb.service.service_runtime import get_qweb_runtime

    runtime = get_qweb_runtime()
    service = runtime.services.components.get(component)
    if service is not None:
        if isinstance(service, ret_type):
            return service
        hastype = type(service)
        raise TypeError(f"Backend has invalid type: {component} -> {hastype}")
    raise ValueError(f"Backend is None: {service}")


async def run_system_task(
    name: str,
    id_owner: int,
    id_object: str = "",
    id_instance: str = "",
    args: dict = {},
) -> Optional[ScheduledTask]:
    from app.qweb.service.service_tasks import QwebTaskManager
    from app.qweb.common.common import SystemTaskArgs

    mancomp: QwebTaskManager = await get_service(ServiceComponent.TASK, QwebTaskManager)
    task = mancomp.get_task_system(name)
    if task != "":
        sysargs = SystemTaskArgs(args, "", id_object, id_instance)
        newtask = (task, [sysargs], {})
        return await mancomp.start_systask(
            name, newtask, True, id_owner, id_object, id_instance
        )
    return None


# async def run_systask(
#     self,
#     name: str,
#     ctx: QwebProcessorContexts,
#     proc_request: ProcessorRequest,
#     info,
#     user,
# ):
#     """Runs registerable system task"""
#     from app.qweb.common.common import TaskArgs
#
#     mancomp: QwebTaskManager = ctx.core.get(ServiceComponent.TASK)
#     task = mancomp.get_task_system(name)
#     if task != "":
#         args = TaskArgs(ctx, proc_request, info, user)
#         newtask = (task, [args], {})
#         return await mancomp.run_systask_concurrently(newtask)
#     return {}


async def get_database(ret_type: Type[T]) -> T:
    from app.daas.db.database import Database

    dbase = Database()
    await dbase.connect()
    if isinstance(dbase, ret_type):
        return dbase
    raise ValueError(f"DB-Backend has invalid type: {dbase}")
