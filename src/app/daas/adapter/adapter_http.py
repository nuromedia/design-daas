"""A adapter  to fetch Http requests"""

import aiohttp
import json as json_parser
from dataclasses import dataclass
from typing import Any
import urllib3
import ssl
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class HttpAdapterConfig:
    """
    HttpAdapterConfig
    """

    verify_tls: bool
    logging: bool
    logrequests: bool
    logresults: bool


# pylint: disable=too-few-public-methods
class HttpAdapter(Loggable):
    """Http adapter to retrieve local requests"""

    def __init__(self, cfg: HttpAdapterConfig) -> None:
        Loggable.__init__(self, LogTarget.HTTP)
        self.config = cfg
        if self.config.verify_tls is False:
            urllib3.disable_warnings()

    # pylint: disable=too-many-arguments,unused-argument,dangerous-default-value
    async def request(
        self,
        method: str,
        url: str,
        header: dict[str, str] = {},
        cookies: dict[str, str] = {},
        params: dict[str, str] = {},
        data: dict[str, Any] = {},
        files: dict[str, Any] = {},
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Perform request with specified parameters
        """
        encoded_data: dict[str, Any] | str = data
        if "Content-Type" in header:
            if header["Content-Type"] == "application/json":
                encoded_data = json_parser.dumps(data)
        if await self.__check_request_method(method):
            args = {
                "method": method.upper(),
                "url": url,
                "params": params,
            }
            if method.lower() != "get":
                args.update(data=encoded_data)
            return await self._request_aio(method, url, header, args, cookies, files)
        self._log_error(f"Method {method} not known for {url}")
        raise ValueError(f"Specified method was not known: '{method.upper()}'")

    # pylint: disable=too-many-arguments,unused-argument
    async def _request_aio(
        self,
        method: str,
        url: str,
        header: dict,
        args: dict,
        cookies: dict,
        files: dict,
    ) -> tuple[aiohttp.ClientResponse, dict]:

        try:
            ssl_context = ssl.create_default_context()
            if self.config.verify_tls is False:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    **args, headers=header, cookies=cookies, ssl=ssl_context
                ) as response:
                    await self.__print_response(method, url, response)
                    result = response
                    if response.content_type.startswith("application/json"):
                        data = await response.json()  # Mandatory: within context!
                        return response, data
                    else:
                        return result, {}
        except Exception as e:
            self._log_error(f"Unexpected aiohttp error: {str(e)}")
            raise

    async def __check_request_method(self, method: str) -> bool:
        if method.lower() in [
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "options",
            "head",
        ]:
            return True
        return False

    async def __print_response(self, method: str, url: str, response) -> None:
        if response is not None:
            msg = ""
            if self.config.logrequests:
                msg = f"{method.upper():>6} {url}"
            if self.config.logresults and response.status == 200:
                body = json_parser.dumps(await response.json(), indent=1)
                msg = f"{msg}\n{body}"
            if msg != "":
                self._log_info(msg, response.status)
