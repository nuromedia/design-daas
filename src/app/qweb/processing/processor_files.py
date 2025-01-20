"""File processor"""

import os
from quart import Response, send_from_directory
from app.qweb.common.config import QuartProcessorConfig
from app.qweb.processing.processor import (
    FileProcessorAction,
    ProcessorBase,
    ProcessorRequest,
)
from app.qweb.service.service_context import QwebProcessorContexts


class FileProcessor(ProcessorBase):
    """File processor"""

    async def process(
        self, ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info, user
    ) -> tuple[Response | dict | str, int]:
        """Process output"""
        file = proc_request.path
        action = proc_request.action
        if action == FileProcessorAction.ROOT_FILE:
            path = os.getcwd() + f"/{self.cfg_quart.webroot_folder}"  # "/data/webroot"
        elif action == FileProcessorAction.STATIC_FILE:
            path = os.getcwd() + f"/{self.cfg_quart.static_folder}"
        else:
            code = 500
            return (
                self.create_error_response(
                    msg=f"Invalid action for FileProcessor: {action}",
                    status=code,
                    content_type=proc_request.content_type,
                ),
                code,
            )
        result = self.create_async_response(send_from_directory(path, file))
        if isinstance(result, Response):
            return (
                Response(
                    response=result.response,
                    status=200,
                    content_type=proc_request.content_type,
                ),
                200,
            )
        return (
            Response(
                response=result,
                status=200,
                content_type=proc_request.content_type,
            ),
            200,
        )
