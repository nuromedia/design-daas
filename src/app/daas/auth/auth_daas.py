"""DaaS authenticator base"""

import logging
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass
from app.daas.common.model import (
    Application,
    DaasObject,
    Environment,
    File,
    RessourceInfo,
)
from app.daas.objects.object_instance import InstanceObject
from app.qweb.auth.auth_qweb import QwebAuthenticatorBase, QwebUser
from app.qweb.common.config import QwebAuthenticatorConfig
from app.qweb.common.qweb_tools import get_database
from app.qweb.logging.logging import LogTarget


@dataclass
class AuthenticatorConfig:
    """Config for authenticator"""

    url: str
    clientid: str
    scope: str
    username: str
    password: str
    verify_endpoints: bool
    remote_verification: bool
    logrequests: bool


@dataclass
class AuthToken:
    """A token"""

    refresh_token: str = ""
    access_token: str = ""
    time_valid: int = 0
    created_at: datetime = datetime.now()
    valid_until: datetime = datetime.now()


class DaasAuthenticatorBase(QwebAuthenticatorBase):
    """DaaS authenticator base"""

    config: QwebAuthenticatorConfig

    def __init__(self, cfg_auth: QwebAuthenticatorConfig):
        self.cfg_auth = cfg_auth
        self.logger = logging.getLogger(LogTarget.AUTH.value)
        QwebAuthenticatorBase.__init__(self, cfg_auth)

    async def verify_entity_ownership(self, entity: Optional[Any], owner: int) -> bool:
        """Tests if owner has permissions to access entity properties"""
        if self.cfg_auth.enable_entity_verification:
            if isinstance(entity, DaasObject):
                return await self.verify_object(entity, owner)
            elif isinstance(entity, InstanceObject):
                return await self.verify_instance(entity, owner)
            elif isinstance(entity, Environment):
                return await self.verify_environment(entity, owner)
            elif isinstance(entity, File):
                return await self.verify_file(entity, owner)
            elif isinstance(entity, Application):
                return await self.verify_app(entity, owner)
            elif isinstance(entity, RessourceInfo):
                return await self.verify_limit(entity, owner)
            elif isinstance(entity, dict):
                return await self.verify_dict(entity, owner)
            elif isinstance(entity, list):
                return await self.verify_list(entity, owner)
            if self.config.enable_log_entity_verification:
                self._log_info("Verifying ownership error: Invalid entity type")
            return False
        if self.config.enable_log_entity_verification:
            self._log_info(f"Verifying ownership disabled: {True} for owner {owner}")
        return True

    async def verify_limit(self, entity: RessourceInfo, owner: int) -> bool:
        testid = entity.id_owner
        result = testid in (-1, 0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership ( lmt): {result} for {owner} and {entity}"
            )
        return result

    async def verify_list(self, entity: list, owner: int) -> bool:
        result = True
        for element in entity:
            if isinstance(element, dict):
                if "id_owner" in element:
                    testid = element["id_owner"]
                    result = testid in (0, owner)
                    if result is False:
                        break
                else:
                    result = True
            else:
                result = False
                break
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership (list): {result} for {owner} and {entity}"
            )
        return result

    async def verify_dict(self, entity: dict, owner: int) -> bool:
        result = True
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership (dict): {result} for {owner} and {entity}"
            )
        return result

    async def verify_object(self, entity: DaasObject, owner: int) -> bool:
        testid = entity.id_owner
        result = testid in (0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership ( obj): {result} for {owner} and {testid}"
            )
        return result

    async def verify_instance(self, entity: InstanceObject, owner: int) -> bool:
        testid = entity.app.id_owner
        result = testid in (0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership (inst): {result} for {owner} and {testid}"
            )
        return result

    async def verify_environment(self, entity: Environment, owner: int) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        testobj = await dbase.get_daas_object(entity.id_object)
        assert testobj is not None
        testid = testobj.id_owner
        result = testid in (0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership (inst): {result} for {owner} and {testid}"
            )
        return result

    async def verify_file(self, entity: File, owner: int) -> bool:
        testid = entity.id_owner
        result = testid in (0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership (file): {result} for {owner} and {testid}"
            )
        return result

    async def verify_app(self, entity: Application, owner: int) -> bool:
        from app.daas.db.database import Database

        dbase = await get_database(Database)
        testid = entity.id_owner
        result = testid in (0, owner)
        if result and entity.id_template is not None and entity.id_template != "":
            testfile = await dbase.get_daas_object(entity.id_template)
            if testfile is not None:
                result = testfile.id_owner in (0, owner)
        if result and entity.id_file is not None and entity.id_file != "":
            testfile = await dbase.get_file(entity.id_file)
            if testfile is not None:
                result = testfile.id_owner in (0, owner)
        if self.config.enable_log_entity_verification:
            self._log_info(
                f"Verifying ownership ( app): {result} for {owner} and {testid}"
            )
        return result

    async def return_default_user(self, authenticated: bool = True) -> QwebUser:
        return QwebUser(
            self.config.local.default_userid,
            self.config.local.default_username,
            authenticated,
        )

    async def initialize(self) -> bool:
        """Initialize component"""
        return True
