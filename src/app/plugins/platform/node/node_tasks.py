"""Node Tasks"""

from quart import Response
from app.daas.common.ctx import get_backend_component, get_request_object
from app.daas.node.nodecontrol import NodeController
from app.daas.objects.object_instance import InstanceObject
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.blueprints.blueprint_info import BlueprintInfo
from app.qweb.processing.processor import ProcessorRequest
from app.qweb.service.service_context import QwebProcessorContexts
from enum import Enum


class NodeTask(Enum):
    """Node processor tasktype"""

    NODE_CONFIGURE_DHCP = "NODE_CONFIGURE_DHCP"
    NODE_CONFIGURE_IPTABLES = "NODE_CONFIGURE_IPTABLES"
    NODE_INVOKE_UPLOAD = "NODE_INVOKE_UPLOAD"


async def configure_dhcp(
    ctx: QwebProcessorContexts,
    proc_request: ProcessorRequest,
    info: BlueprintInfo,
    user: QwebUser,
) -> Response | dict | str:
    """Configure dhcp"""
    entity = get_request_object(ctx, "entity", InstanceObject)
    nodecon = get_backend_component(ctx, "node", NodeController)
    code, str_out, str_err = nodecon.node_vmconfigure_dhcp(
        entity.app.id_proxmox, entity.host
    )
    return {"success": code, "syslog": f"{str_out}{str_err}"}


async def configure_iptables(
    ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info: BlueprintInfo
) -> Response | dict | str:
    """Configure iptables"""
    entity = get_request_object(ctx, "entity", InstanceObject)
    nodecon = get_backend_component(ctx, "node", NodeController)
    code, str_out, str_err = nodecon.node_vmconfigure_iptables(entity.host)
    return {"success": code, "syslog": f"{str_out}{str_err}"}


async def invoke_upload(
    ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info: BlueprintInfo
) -> Response | dict | str:
    """Configure dhcp"""
    #     # Upload2host
    #     code = 0
    #     str_out = ""
    #     str_err = ""
    #     # Upload dockerfile
    #     store = await ctx.get_filestore()
    #     name = args["file"].filename
    #     userid = await get_userid(ctx)
    #
    #     stored = await store.upload_user_file_upload(args["file"], name, userid)
    #     if stored:
    #         str_out = await store.get_user_file_upload(name, userid)
    #
    #     return respond_json(
    #         request,
    #         str(args),
    #         200 if code == 0 else 405,
    #         sys_exitcode=code,
    #         sys_log=f"{str_out}{str_err}",
    #     )
    # return {"Error": "Unknown error"}
    raise NotImplementedError("invoke_upload is not implemented")
