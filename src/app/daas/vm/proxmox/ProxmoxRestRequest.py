import time
import datetime
import json as json_parser
import aiohttp
from typing import Optional
from dataclasses import dataclass
from quart.utils import run_sync
from app.daas.adapter.adapter_http import HttpAdapter, HttpAdapterConfig
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class ProxmoxRestConfig:
    apiuser: str
    apipass: str
    apiurl: str
    sessionurl: str
    session_lifetime: int


class ProxmoxRestRequest(Loggable):
    def __init__(
        self,
        cfgRest: ProxmoxRestConfig,
        cfgHttp: HttpAdapterConfig,
    ):
        Loggable.__init__(self, LogTarget.VM)
        self.configRest = cfgRest
        self.configHttp = cfgHttp
        self.currentSession: Optional[dict] = None
        self.rest = HttpAdapter(self.configHttp)

    # pylint: disable=too-many-arguments
    async def session_request_async(
        self,
        method: str,
        url: str,
        params: dict,
        data: dict,
        files: dict,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Perform HTTP request against specified REST service.
        Uses credentials obtained in a prior session handshake.
        """
        result = None
        credentials = await self.__create_session()
        assert credentials is not None
        hdr = {
            "CSRFPreventionToken": credentials["token"],
            "Cookie": f"PVEAuthCookie={credentials['cookie']}",
        }
        cookies = {}  # {"PVEAuthCookie": credentials["cookie"]}
        fullurl = f"{self.configRest.apiurl}/{url}"
        if method in ["post", "put"]:
            if len(files) == 0:
                hdr["Content-Type"] = "application/json"
        result, data = await self.rest.request(
            method=method,
            url=fullurl,
            header=hdr,
            cookies=cookies,
            params=params,
            data=data,
            files=files,
        )
        return result, data

    # pylint: disable=too-many-arguments
    async def session_request_sync(
        self,
        method: str,
        vmnode: str,
        url: str,
        params: dict,
        data: dict,
        files: dict,
    ) -> tuple[aiohttp.ClientResponse, dict]:
        response, json = await self.session_request_async(
            method, url, params, data, files
        )
        self.__log_request(response, json)
        if response is not None and response.status >= 200 and response.status < 300:
            json_data = json["data"]
            if isinstance(json_data, str) and json_data != "":
                resp, data = await self.__read_task_sync(vmnode, 1, json_data)
                return resp, data
        return response, json

    async def __create_session(self) -> Optional[dict]:
        """
        Create session within proxmox by specifying username and password
        Returns CSRF-Token and access cookie for usage in subsequent requests.
        """
        if self.currentSession is not None:
            ts_session = self.currentSession["time"]
            ts_now = datetime.datetime.now().timestamp()
            ts_diff = ts_now - ts_session
            # self._log_info(f"Session lifetime: {ts_diff}")
            if ts_diff > self.configRest.session_lifetime:
                self._log_info(f"Reset Session: {ts_diff}")
                self.currentSession = None

        if self.currentSession is None:
            response, data = await self.rest.request(
                method="post",
                url=f"{self.configRest.apiurl}/{self.configRest.sessionurl}",
                header={},
                cookies={},
                params={},
                data={
                    "username": f"{self.configRest.apiuser}",
                    "password": f"{self.configRest.apipass}",
                },
                files={},
            )
            session = await self.__check_session_response(response, data)
            if session["token"] != "" and session["cookie"] != "":
                self.currentSession = session
        return self.currentSession

    async def __check_session_response(self, response, data) -> dict:
        """
        Checks if response for authorization was valid.
        Returns CSRF-Token and access cookie for usage in subsequent requests.
        """

        cur_time = datetime.datetime.now().timestamp()
        result = {
            "token": "",
            "cookie": "",
            "time": cur_time,
        }
        if response is not None and response.status == 200:
            json = data
            if json != "" and "data" in json:
                data = json["data"]
                if "CSRFPreventionToken" in data and "ticket" in data:
                    result = {
                        "token": data["CSRFPreventionToken"],
                        "cookie": data["ticket"],
                        "time": cur_time,
                    }
            # self._log_info(f"{response.status:3} -> Session created: {cur_time}")
        return result

    async def __read_task_sync(
        self, vmnode: str, intervall: int, upid: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Reads task status via proxmox api ()
        """

        while True:
            result, data = await self.__read_task_async(vmnode, upid)
            if result is not None and len(data) > 0:
                return result, data
            time.sleep(intervall)

    async def __read_task_async(
        self, vmnode: str, upid: str
    ) -> tuple[aiohttp.ClientResponse, dict]:
        """
        Reads task status via proxmox api ()
        """
        url = f"nodes/{vmnode}/tasks/{upid}/status"
        response, json = await self.session_request_async(
            "get", url, params={}, data={}, files={}
        )
        if response is not None and response.status == 200:
            json_data = json["data"]
            if "status" in json_data:
                if json_data["status"] == "stopped":
                    return response, json_data
        if response is not None and response.status == 500:
            msg = f"ERROR Response: {json}"
            self._log_info(msg)
        return response, {}

    def __log_request(self, response, data):
        if response is None:
            return
        if response.status >= 200 and response.status < 300:
            method = response.request_info.method
            msg = ""
            if self.configHttp.logrequests:
                msg = " ".join(
                    [
                        f"{response.status:3}",
                        f"-> {method.upper():>6} {response.request_info.url}",
                    ]
                )
            if self.configHttp.logresults and response.status == 200:
                body = json_parser.dumps(data, indent=1)
                msg = f"{msg} \n{body}"
            if msg != "":
                self._log_info(msg)
