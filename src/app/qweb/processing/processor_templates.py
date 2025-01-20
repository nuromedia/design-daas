"""Template processor"""

from quart import Response, render_template
from app.qweb.processing.processor import (
    TemplateProcessorAction,
    ProcessorBase,
    ProcessorRequest,
)
from app.qweb.service.service_context import QwebProcessorContexts


class TemplateProcessor(ProcessorBase):
    """Template processor"""

    async def process(
        self, ctx: QwebProcessorContexts, proc_request: ProcessorRequest, info, user
    ) -> tuple[Response | dict | str, int]:
        """Process output"""
        action = proc_request.action
        path = ""
        if action == TemplateProcessorAction.STATIC_HTML:
            path = proc_request.path
        elif action == TemplateProcessorAction.STATIC_JS:
            path = proc_request.path
        elif action == TemplateProcessorAction.STATIC_CSS:
            path = proc_request.path
        else:
            code = 500
            return (
                self.create_error_response(
                    msg=f"Invalid action for FileProcessor: {action}",
                    status=code,
                    content_type=proc_request.content_type,
                ),
                500,
            )
        result = self.create_async_response(
            render_template(
                path,
                **self.template_args,
                **proc_request.static_args,
                **proc_request.request_context.request_args,
            )
        )
        if isinstance(result, str):
            result = Response(
                response=result,
                status=200,
                content_type=proc_request.content_type,
            )
        if isinstance(result, Response):
            result.content_type = proc_request.content_type
        return result, 200
