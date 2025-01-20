"""Websocket processor"""

from typing import Any
from quart import Response
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.processing.processor import (
    ProcessorBase,
    ProcessorRequest,
    WebsocketProcessorAction,
)
from app.qweb.service.service_context import QwebProcessorContexts
from app.qweb.blueprints.blueprint_info import BlueprintInfo


class WebsocketProcessor(ProcessorBase):
    """Websocket processor"""

    async def process(
        self,
        ctx: QwebProcessorContexts,
        proc_request: ProcessorRequest,
        info: BlueprintInfo,
        user: QwebUser,
    ) -> tuple[Response | dict | str, int]:
        """Process output"""

        action = proc_request.action
        status = 500
        data: Response | str | dict[str, Any] = ""
        if action == WebsocketProcessorAction.VIEWER:
            data, code = await self.__create_html_result(ctx, proc_request, info, user)
            status = code
        if action == WebsocketProcessorAction.EXTENSION:
            data, code = await self.__create_html_result(ctx, proc_request, info, user)
            status = code
        else:
            return (
                self.create_error_response(
                    msg=f"Invalid action for WebsocketProcessor: {action}",
                    status=status,
                    content_type=proc_request.content_type,
                ),
                status,
            )
        return data, status

    async def __create_html_result(
        self,
        ctx: QwebProcessorContexts,
        proc_request: ProcessorRequest,
        info: BlueprintInfo,
        user: QwebUser,
    ) -> tuple[str | Response, int]:
        if proc_request.apitask != "":
            try:
                ret = await self.run_apitask(ctx, proc_request, info, user)
                if isinstance(ret, str):
                    return ret, 200
            except Exception as exe:
                resp = self.create_error_response("Exception in ApiProcessor (HTML)")
                self._log_error("Exception in ApiProcessor (HTML): ", 2, exe)
                return resp, 500
        msg = f"No processor task configured for {info.name}"
        self._log_error(msg, 1)
        resp = self.create_error_response(msg)
        return resp, 500
