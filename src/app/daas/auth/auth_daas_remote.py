"""Authenticates requests"""

import aiohttp
from typing import Optional
from datetime import datetime, timedelta
from app.daas.adapter.adapter_http import HttpAdapter, HttpAdapterConfig
from app.daas.auth.auth_daas import AuthToken, DaasAuthenticatorBase
from app.qweb.auth.auth_qweb import QwebUser
from app.qweb.blueprints.blueprint_info import AuthenticationMode, BlueprintInfo
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.common.qweb_tools import get_database
from app.qweb.processing.processor import ProcessorRequest


class DaasRemoteAuthenticator(DaasAuthenticatorBase):
    """Remote authenticator"""

    config: QwebAuthenticatorConfig

    def __init__(self, cfg_auth: QwebAuthenticatorConfig, cfg_http: HttpAdapterConfig):
        self.cfg_http = cfg_http
        self.adapter = HttpAdapter(self.cfg_http)
        self.token: Optional[AuthToken] = None
        DaasAuthenticatorBase.__init__(self, cfg_auth)

    async def initialize(self) -> bool:
        """Initialize component"""
        return True

    async def verify_user(self, req: ProcessorRequest, info: BlueprintInfo) -> QwebUser:
        """Verifies only user"""

        result = QwebUser()
        if self.cfg_auth.enable_auth_token:
            if (
                info.auth_params == AuthenticationMode.TOKEN
                or info.auth_params == AuthenticationMode.ALL
            ):
                result = await self.get_user_by_viewer_token(req)
                if result.authenticated:
                    return result

        if self.config.enable_auth_user:
            userdict = await self.get_user_session(req.bearer)
            if userdict is not None:
                if "user_id" in userdict and "name" in userdict:
                    result = QwebUser(
                        id_user=userdict["user_id"],
                        name=userdict["name"],
                        authenticated=True,
                    )
                    self._log_request(
                        f"200 ->   HTTP Remote Auth success for user '{result.id_user}'"
                    )
                    return result
        self._log_error("HTTP Remote Auth error", 1)
        return result

    async def verify_endpoint(
        self, req: ProcessorRequest, info: BlueprintInfo
    ) -> QwebUser:
        """Verifies endpoint"""
        result = QwebUser()
        user = await self.verify_user(req, info)
        if user.authenticated and self.config.enable_auth_endpoint:

            response_remote = await self.get_endpoint_permission(
                info.name, user.id_user
            )
            if (
                response_remote is not None
                and "result" in response_remote
                and "user" in response_remote
            ):
                if response_remote["result"] == "allow":
                    name = response_remote["user"]["name"]
                    userid = response_remote["user"]["id"]
                    result = QwebUser(id_user=userid, name=name, authenticated=True)
                    self._log_request(
                        f"200 ->   HTTP Remote Auth success for endpoint '{info.name}'"
                    )
                    return result
            self._log_error(" -1 ->   HTTP Remote Auth error")
        return result

    async def get_user_session(self, bearer: str) -> dict:
        """Verify bearer"""
        url = f"{self.cfg_auth.remote.url}/oauth2/user/session"
        response, data = await self.__request_api("get", url, access_token=bearer)
        if response is None or response.status != 200:
            self._log_error(f"Backend-Auth error on {url}", response.status)
            return {}
        return data

    async def get_user_by_viewer_token(self, req: ProcessorRequest) -> QwebUser:
        """Verify viewer token"""
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        result = await self.return_default_user(False)
        if self.cfg_auth.enable_auth_token:
            reqargs = req.request_context.request_args
            token = ""
            if "token" in reqargs:
                token = reqargs["token"]
                con = await dbase.get_guacamole_connection_by_token(token)
                if con is not None:
                    inst = await dbase.get_instance_by_conid(con.id)
                    if inst is not None:
                        userid = inst.id_owner
                        result = QwebUser(userid, token, True)
                self._log_request(
                    f"200 ->   HTTP Remote Auth success for user '{result.id_user}'"
                )
                return result
        return result

    async def get_endpoint_permission(self, endpoint: str, userid: int) -> dict:
        """Get user details"""
        endpoint = "debug"
        url = f"{self.cfg_auth.remote.url}/permissions/{endpoint}/{userid}"
        response, data = await self.__request_api("get", url)
        if response is None or response.status != 200:
            self._log_error(f"Backend-Auth error on {url}", response.status)
            return {}
        return data

    async def get_endpoint_permission_by_viewer_token(
        self, endpoint: str, token: str
    ) -> dict:
        return {}

    async def get_endpoint_permission_by_bearer(
        self, endpoint: str, bearer: str
    ) -> dict:
        """Get user details"""
        url = f"{self.cfg_auth.remote.url}/permissions_info"
        endpoint_name = endpoint
        if endpoint_name.startswith("/"):
            endpoint_name = endpoint_name[1:]

        # data = {"token": bearer, "function_name": endpoint_name}
        data = {"token": bearer, "function_name": "debug"}
        response, resp_data = await self.__request_api(
            "post", url, access_token=bearer, data=data
        )
        if response is None or response.status != 200:
            if response is not None:
                resp = await response.json()
                self._log_error(f"Bearer: {bearer}")
                self._log_error(f"Response: {resp}")
            self._log_error(f"Backend-Auth error on {url}")
            return {}
        result = resp_data
        return result

    async def refresh_session(self) -> tuple:
        """Obtaines new token from authentication service"""

        # Check existing token
        if self.token is not None:
            self.__check_token()

        # Fetch new if required
        if self.token is None:
            response, data = await self.__request_token()
            if response is None or response.status != 200:
                self._log_error("Error on token request")
                return 1, "", "Authentication error"
            # data = await response.json()
            self.__create_token(data)

        # Create response
        if self.token is None:
            self._log_error("Error token is None")
            return 1, "", "Authentication error"
        return 0, "", ""

    # pylint: disable=dangerous-default-value
    async def __request_api(
        self, method: str, url: str, *, access_token: str = "", data: dict = {}
    ) -> tuple[aiohttp.ClientResponse, dict]:
        chosen = await self.__choose_bearer_token(access_token)
        header = {
            "Authorization": f"Bearer {chosen}",
            "accept": "application/json",
        }
        if len(data) > 0:
            header["Content-Type"] = "application/json"
        return await self.adapter.request(method, url, header=header, data=data)

    async def __choose_bearer_token(self, access_token: str) -> str:
        if access_token == "":
            if self.token is None:
                await self.refresh_session()
            if self.token is not None:
                return self.token.access_token
            return ""
        return access_token

    async def __request_token(self):
        # self.__log_request("Creating new token!")
        url = f"{self.cfg_auth.remote.url}/oauth2/user/token"
        response, data = await self.adapter.request(
            method="post",
            url=url,
            header={"accept": "application/json"},
            cookies={},
            params={},
            data={
                "username": self.cfg_auth.remote.username,
                "password": self.cfg_auth.remote.password,
                "client_id": self.cfg_auth.remote.clientid,
                "grant_type": "password",
                "scope": self.cfg_auth.remote.scope,
            },
        )
        return response, data

    def __check_token(self):
        if self.token is not None:
            if datetime.now() < self.token.valid_until:
                pass
            else:
                obj = self.token.valid_until
                fmt = obj.strftime("%Y-%m-%d %H:%M:%S")
                self._log_request(f"Token expired at: {fmt}")
                self.token = None

    def __create_token(self, data: dict):
        if "token_type" in data and "expires_in" in data:
            if "refresh_token" in data and "access_token" in data:
                now = datetime.now()
                self.token = AuthToken(
                    created_at=now,
                    valid_until=now + timedelta(seconds=data["expires_in"]),
                    time_valid=data["expires_in"],
                    refresh_token=data["refresh_token"],
                    access_token=data["access_token"],
                )
                obj = self.token.valid_until
                fmt = obj.strftime("%Y-%m-%d %H:%M:%S")
                self._log_request(f"New token expires at: {fmt}")

    def _log_request(self, msg: str) -> None:
        if self.cfg_auth.enable_logging:
            self._log_info(msg)
