"""Handles blueprints"""

import asyncio
from types import FrameType
from typing import Any, Optional
from quart import Blueprint, Response, request, websocket
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.blueprints.blueprint_handler_base import BlueprintHandlerBase
from app.qweb.blueprints.blueprint_info import (
    AuthenticationMode,
    BlueprintInfo,
    ConcurrencyMode,
)
from app.qweb.processing.processor import (
    ApiProcessorAction,
    FileProcessorAction,
    ProcessorRequest,
    ProcessorType,
    TemplateProcessorAction,
    WebsocketProcessorAction,
)
from app.qweb.service.service_context import (
    QwebProcessorContexts,
    ServiceComponent,
)
from app.qweb.common.timings import Measurement
from app.qweb.service.service_tasks import QwebTaskManager

DELAY_CTX = 0.0


class BlueprintHandler(BlueprintHandlerBase):
    """Handles Blueprints"""

    def __init__(
        self,
        blueprints: Blueprint,
        infos: list[BlueprintInfo],
        testing: bool,
        default_handler: Optional[Any],
    ):

        BlueprintHandlerBase.__init__(
            self,
            blueprints=blueprints,
            infos=infos,
            testing=testing,
            default_handler=default_handler,
        )

    async def handle_frame(
        self, frame: Optional[FrameType]
    ) -> tuple[Response | dict | str, int]:
        """Handles requests"""

        # Init frame
        timing = await self._init_timing()
        framename = self._get_frame_name(frame)
        if framename == "":
            self._log_error(f"Invalid framename: {framename}", 1)
            return self._create_error_response("Invalid frame name", 500)

        # handle frame
        result, code = await self.__try_handle_frame(framename, timing)
        if result is None:
            return self._create_error_response("Response was None", 500)

        # Finalize frame
        await self._append_timing(result, timing)
        return result, code

    async def __try_handle_frame(self, framename: str, timing: Optional[Measurement]):
        status_http = 500
        status_sys = 500
        try:
            result, status_http = await self.__handle_request_stages(framename, timing)
        except Exception as exe:
            msg = "Exception in BlueprintHandler"
            ctype = await self.get_requested_content_type()
            self._log_error(f"{msg}:", status_sys, exe)
            return self._create_error_response(
                msg=msg,
                content_type=ctype,
                status_http=status_http,
                status_sys=status_sys,
                exception=exe,
            )
        return result, status_http

    async def get_requested_content_type(
        self, info: Optional[BlueprintInfo] = None
    ) -> str:
        result = "text/html"
        if info is not None:
            if info.websocket_request is False:
                hdr_accept = request.headers.get("Accept")
            else:
                hdr_accept = websocket.headers.get("Accept")
            if hdr_accept is not None:
                result = hdr_accept
        else:
            try:
                hdr_accept = request.headers.get("Accept")
                if hdr_accept is not None:
                    result = hdr_accept
            except Exception:
                pass

        return result

    async def __handle_request_stages(
        self, name: str, timing: Optional[Measurement]
    ) -> tuple[Response | dict | str, int]:
        """Handles individual requests"""
        result = {}, 500

        # Prepare
        info, req = await self._prepare_stage(name)
        if info is None or req is None:
            self._log_error("Handler could not prepare stage", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                "Blueprint handler could not prepare context", 500, content_type=ctype
            )

        # Check concurrency mode
        mode = info.conc_params
        if mode == ConcurrencyMode.NONE:
            result = await self.sequential_stages(req, info, timing)
        elif mode == ConcurrencyMode.CTX_AND_AUTH:
            result = await self.concurrent_ctx_and_auth(req, info, timing)
        elif mode == ConcurrencyMode.AUTH_AND_PROC:
            result = await self.concurrent_auth_and_proc(req, info, timing)

        self._log_request(info=info, req=req, timing=timing)
        return result

    async def sequential_stages(
        self,
        req: ProcessorRequest,
        info: BlueprintInfo,
        timing: Optional[Measurement],
    ) -> tuple[Response | dict | str, int]:
        """Sequential evaluation of auth and processing"""

        # Contexts
        if timing is not None:
            timing.context.start()
        ctx = await self.task_context(info, req, timing)
        if ctx is None:
            self._log_error("Sequential stage error during task_context()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                "ServiceContext unavailble", 500, content_type=ctype
            )

        # Auth
        if timing is not None:
            timing.authentication.start()
        authres = await self.task_authentication(info, req, timing)
        if authres.authenticated is False:
            self._log_error("Sequential stage error during task_authentication()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                "Authentication error", 403, content_type=ctype
            )

        # Onership
        verified = await self.__verify_entity_ownerships(
            ctx.objects.objects, authres.id_user
        )
        if verified is False:
            self._log_error("Error during ownership_verify (seq)", 2)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                f"Invalid owner: {authres.id_user}", 500, content_type=ctype
            )

        # Processing
        if timing is not None:
            timing.processing.start()
        procres = await self.task_processing(ctx, req, info, timing, authres)

        # Result
        res, code = procres
        if isinstance(res, Response):
            res.content_type = info.content_type

        return res, code

    async def concurrent_ctx_and_auth(
        self,
        req: ProcessorRequest,
        info: BlueprintInfo,
        timing: Optional[Measurement],
    ) -> tuple[Response | dict | str, int]:
        """Concurrent evaluation of auth and processing"""

        tasks = [
            (self, "task_context", [info, req, timing], {}),
            (self, "task_authentication", [info, req, timing], {}),
        ]

        # Run tasks
        if timing is not None:
            timing.authentication.start()
            timing.context.start()
        taskman = await self._get_taskmanager()
        results = await taskman.run_tasks_concurrently(tasks)

        # Evaluate results
        ctxres, authres = results
        if authres.authenticated is False:
            self._log_error("ctx-auth error during task_authenitcation()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                "Authentication error", 403, content_type=ctype
            )

        # Prepare tasks
        if ctxres is None:
            self._log_error("ctx-auth error during task_context()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response("ServiceContext unavailable", 500)

        # Onership
        verified = await self.__verify_entity_ownerships(
            ctxres.objects.objects, authres.id_user
        )
        if verified is False:
            self._log_error("Error during ownership_verify (ctx-auth)", 2)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                f"Invalid owner: {authres.id_user}", 500, content_type=ctype
            )

        # Processing
        if timing is not None:
            timing.processing.start()
        procres = await self.task_processing(ctxres, req, info, timing, authres)

        ctype = await self.get_requested_content_type(info)
        res, code = procres
        if isinstance(res, Response):
            res.content_type = info.content_type
        return res, code

    async def concurrent_auth_and_proc(
        self,
        req: ProcessorRequest,
        info: BlueprintInfo,
        timing: Optional[Measurement],
    ) -> tuple[Response | dict | str, int]:
        """Concurrent evaluation of auth and processing"""

        # Contexts
        if timing is not None:
            timing.context.start()
        ctx = await self.task_context(info, req, timing)
        if ctx is None:
            self._log_error("auth-proc error during task_context()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                "ServiceContext unavailable", 500, content_type=ctype
            )
        if timing is not None:
            timing.context.stop()

        # Prepare tasks
        tasks = [
            (self, "task_authentication", [info, req, timing], {}),
            (self, "task_processing", [ctx, req, info, timing, QwebUser()], {}),
        ]

        # Run tasks
        if timing is not None:
            timing.authentication.start()
        if timing is not None:
            timing.processing.start()
        taskman: QwebTaskManager = ctx.core.get(ServiceComponent.TASK)
        results = await taskman.run_tasks_concurrently(tasks)

        # Evaluate results
        authres, procres = results
        if authres.authenticated is False:
            self._log_error("auth-proc error during task_authentication()", 1)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                f"Procargs not created {authres} {procres}", 500, content_type=ctype
            )

        # Onership
        verified = await self.__verify_entity_ownerships(
            ctx.objects.objects, authres.id_user
        )
        if verified is False:
            self._log_error("Error during ownership_verify (auth-proc)", 2)
            ctype = await self.get_requested_content_type(info)
            return self._create_error_response(
                f"Invalid owner: {authres.id_user}", 500, content_type=ctype
            )

        ctype = await self.get_requested_content_type(info)
        res, code = procres
        if isinstance(res, Response):
            res.content_type = info.content_type
        return res, code

    async def task_context(
        self,
        info: BlueprintInfo,
        req: ProcessorRequest,
        timing: Optional[Measurement],
    ) -> QwebProcessorContexts:
        """Context task"""
        ctx = await self._get_contexts(info, req)
        if DELAY_CTX > 0 and req.path not in ("baseline0"):
            await self.__sleep(DELAY_CTX)
        if timing is not None:
            timing.context.stop()
        return ctx

    async def task_authentication(
        self,
        info: BlueprintInfo,
        req: ProcessorRequest,
        timing: Optional[Measurement],
    ) -> QwebUser:
        """Authentication task"""

        # Prepare
        result = QwebUser()
        authman = await self._get_authmanager()
        if info.auth_params == AuthenticationMode.NONE:
            result.authenticated = True
        else:
            user = await authman.authenticate(req, info)
            result = user

        # Finalize
        if timing is not None:
            timing.authentication.stop()

        return result

    async def task_processing(
        self,
        ctx: QwebProcessorContexts,
        req: ProcessorRequest,
        info: BlueprintInfo,
        timing: Optional[Measurement],
        user: QwebUser,
    ) -> tuple[Response | dict | str, int]:
        """Page processing task"""
        # Prepare
        result = {}
        code = 500

        # Process result
        if info.processor == ProcessorType.FILE:
            if isinstance(info.processor_action, FileProcessorAction):
                result, code = await self.fileproc.process(ctx, req, info, user)
        if info.processor == ProcessorType.STATIC_TEMPLATE:
            if isinstance(info.processor_action, TemplateProcessorAction):
                result, code = await self.tmplproc.process(ctx, req, info, user)
        if info.processor == ProcessorType.WEBSOCKET:
            if isinstance(info.processor_action, WebsocketProcessorAction):
                result, code = await self.socketproc.process(ctx, req, info, user)

        if info.processor == ProcessorType.API:
            if isinstance(info.processor_action, ApiProcessorAction):
                result, code = await self.apiproc.process(ctx, req, info, user)
                await self._append_echo_args(result, req)
                if timing is not None:
                    timing.processing.stop()
        return result, code

    async def __verify_entity_ownerships(self, objects: dict, owner: int) -> bool:
        for name, obj in objects.items():
            valid = await self.__verify_entity_ownership(obj, owner)
            if valid is False:
                self._log_error(f"Ownership not verified: {name}")
                return False
        return True

    async def __verify_entity_ownership(
        self, entity: Optional[Any], owner: int
    ) -> bool:
        authman = await self._get_authmanager()
        return await authman.verify_entity_ownership(entity, owner)

    async def __sleep(self, time_s: float):
        if time_s > 0:
            await asyncio.sleep(time_s)
