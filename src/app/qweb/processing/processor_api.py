"""Api processor"""

import asyncio
from dataclasses import asdict
import traceback
from types import TracebackType
from typing import Any
from quart import Response
from app.daas.common.errors import ObjectProcessingError
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.processing.processor import (
    ApiProcessorAction,
    QwebResult,
    ProcessorBase,
    ProcessorRequest,
)
from app.qweb.service.service_context import QwebProcessorContexts
from app.qweb.blueprints.blueprint_info import BlueprintInfo

DELAY_PROC = 0.0


class ApiProcessor(ProcessorBase):
    """Api processor"""

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
        if action == ApiProcessorAction.HTML:
            data, code = await self.__create_html_result(ctx, proc_request, info, user)
            status = code
        elif action == ApiProcessorAction.JSON:
            return await self.__create_json_response(ctx, proc_request, info, user)
        else:
            return (
                self.create_error_response(
                    msg=f"Invalid action for ApiProcessor: {action}",
                    status=status,
                    content_type=proc_request.content_type,
                ),
                status,
            )
        return data, status

    async def __create_json_response(
        self,
        ctx: QwebProcessorContexts,
        proc_request: ProcessorRequest,
        info: BlueprintInfo,
        user: QwebUser,
    ) -> tuple[dict, int]:
        await self.__delay(proc_request)
        if proc_request.apitask != "":
            try:
                ret = await self.run_apitask(ctx, proc_request, info, user)
                if isinstance(ret, dict | list):
                    resp = QwebResult(200, ret, 0, "")
                    return asdict(resp), resp.response_code
                if isinstance(ret, QwebResult):
                    return asdict(ret), ret.response_code
                msg = f"Unknown return type: {type(ret)}"
                self._log_error(msg, 1)
                resp = self.create_error_dict(msg)
                return asdict(resp), resp.response_code
            except Exception as exe:
                resp = self.create_error_dict(
                    "Exception in ApiProcessor (JSON)", exception=exe
                )
                self._log_error("Exception in ApiProcessor (JSON): ", 2, exe)
                return asdict(resp), resp.response_code
        msg = f"No processor task configured for {info.name}"
        self._log_error(msg, 1)
        resp = self.create_error_dict(msg)
        return asdict(resp), resp.response_code

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

    async def __delay(self, proc_request: ProcessorRequest):
        if DELAY_PROC > 0 and proc_request.path not in ("baseline0"):
            await self.__sleep(DELAY_PROC)

    async def __sleep(self, time_s: float):
        if time_s > 0:
            await asyncio.sleep(time_s)
