"""Manages ressource limits"""

import logging
from dataclasses import dataclass, fields
from typing import Optional
from app.daas.common.model import RessourceInfo
from app.daas.db.database import Database
from app.daas.resources.info.hostinfo import Hostinfo
from app.daas.resources.info.objectinfo import Objectinfo
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class RessourceLimitsConfig:
    """Config for RessourceLimits"""

    sys_max_vms: int
    sys_max_img: int
    sys_max_obj: int
    sys_cpu_max: int
    sys_mem_max: int
    sys_dsk_max: int
    flb_max_vms: int
    flb_max_img: int
    flb_max_obj: int
    flb_cpu_max: int
    flb_mem_max: int
    flb_dsk_max: int
    enable_overcommit: bool
    enable_fallback_userlimit: bool
    log_verification: bool


class RessourceLimits(Loggable):
    """Manages ressource limits"""

    def __init__(self, config: RessourceLimitsConfig):
        Loggable.__init__(self, LogTarget.LIMIT)
        self.initialized = False
        self.overcommitted = False
        self.config = config
        self.limit_fallback: Optional[RessourceInfo] = None
        self.limit_system: Optional[RessourceInfo] = None
        self.limits_user: dict[int, RessourceInfo] = {}
        self.hosttool = Hostinfo()
        self.objtool = Objectinfo()
        self.dbase = Database()

    async def initialize(self):
        """Initializes system"""
        await self.objtool.initialize()
        await self.dbase.connect()
        limits = await self.dbase.get_all_limits()
        for limit in limits:
            await self.put_user_limit(limit.id_owner, limit)

        self.limit_fallback = RessourceInfo(
            -1,
            self.config.flb_max_vms,
            self.config.flb_max_img,
            self.config.flb_max_obj,
            self.config.flb_cpu_max,
            self.config.flb_mem_max,
            self.config.flb_dsk_max,
        )
        self.limit_system = RessourceInfo(
            -1,
            self.config.sys_max_vms,
            self.config.sys_max_img,
            self.config.sys_max_obj,
            self.config.sys_cpu_max,
            self.config.sys_mem_max,
            self.config.sys_dsk_max,
        )

        self.initialized = await self.verify_configured_limit()
        if self.initialized:
            self._log_info(f"Initialized with: Overcommit={self.overcommitted}")

    async def get_user_limit(self, userid: int) -> Optional[RessourceInfo]:
        """Returns specified user limits if available"""
        limit = await self.dbase.get_limit(userid)
        if limit is not None:
            self._log_info(f"Userlimit found for {userid}")
            return limit
        if self.config.enable_fallback_userlimit:
            self._log_info(f"Userlimit not found for {userid}. Using fallback")
            return self.limit_fallback
        self._log_info(f"Userlimit not found for {userid}")
        return None

    async def remove_user_limit(self, userid: int) -> Optional[RessourceInfo]:
        """Removes specified user limits if available"""
        self._log_info(f"Removing userlimit for {userid}")
        await self.dbase.delete_limit(userid)

    async def put_user_limit(
        self, userid: int, limit: RessourceInfo
    ) -> Optional[RessourceInfo]:
        """Removes specified user limits if available"""
        self._log_info(f"Put userlimit for {userid}")
        await self.dbase.create_limit(limit)

    async def list_user_limits(self) -> list[RessourceInfo]:
        """Removes specified user limits if available"""
        return await self.dbase.get_all_limits()

    async def verify_demand(self, userid: int, demand: RessourceInfo) -> bool:
        """Verfies demand against system and user limits"""
        self.__log_verification("Verify system ressources:")
        check_sys = await self.verify_demand_against_system(demand)
        self.__log_verification("Verify user ressources:")
        check_usr = await self.verify_demand_against_user(userid, demand)
        return check_sys and check_usr

    async def verify_demand_against_user(
        self, userid: int, demand: RessourceInfo
    ) -> bool:
        """Verfies demand against user limits"""
        userlimit = await self.get_user_limit(userid)
        if userlimit is None:
            self.__log_verification(f"No limit configured for user {userid}")
            return True
        objres = await self.objtool.get_objectinfo_user(userid)
        if objres is None:
            self.__log_verification(f"Objectinfo not available for user {userid}")
            return False
        sys_res = RessourceInfo(
            userid,
            objres.object_vms,
            objres.object_images,
            objres.objects,
            objres.utilized_cpus,
            objres.utilized_memory,
            objres.utilized_diskspace,
        )
        sys_res.add(demand)
        return await self.__verify_limits(sys_res, userlimit)

    async def verify_demand_against_system(self, demand: RessourceInfo) -> bool:
        """Verfies demand against system limits"""
        if self.limit_system is None:
            if self.config.log_verification:
                self._log_info("Systemlimit not available")
            return False

        objres = await self.objtool.get_objectinfo_system()
        sys_res = RessourceInfo(
            -1,
            objres.object_vms,
            objres.object_images,
            objres.objects,
            objres.utilized_cpus,
            objres.utilized_memory,
            objres.utilized_diskspace,
        )
        sys_res.add(demand)
        self._log_info(f"Verify objres: {objres}")
        self._log_info(f"Verify sysres: {sys_res}")
        self._log_info(f"Verify demand: {demand}")
        return await self.__verify_limits(sys_res, self.limit_system)

    async def verify_configured_limit(self) -> bool:
        """Verfies configured system limit"""
        if self.limit_system is None:
            self.__log_verification("Systemlimit not available")
            return False
        hostres = await self.hosttool.read_host_ressources()
        objres = await self.objtool.get_objectinfo_system()
        if hostres is not None and objres is not None:
            info_host = RessourceInfo(
                -1,
                -1,
                -1,
                -1,
                hostres.max_cpus,
                hostres.max_memory,
                hostres.max_disk_space_data,
            )
            verified = await self.__verify_limits(self.limit_system, info_host)
            if verified is False and self.config.enable_overcommit is True:
                self.overcommitted = True
                return True
            return verified
        self._log_info(f"Required ressources not vailable: {hostres},{objres}")
        return False

    async def __verify_limits(
        self, demand: RessourceInfo, limit: RessourceInfo
    ) -> bool:
        result = True
        failed = ""
        for field in fields(limit):
            fieldname = field.name
            if fieldname == "id_owner":
                continue

            limit_value = getattr(limit, fieldname)
            demand_value = getattr(demand, fieldname)
            checked = await self.__verify_limit(demand_value, limit_value)
            if checked is False:
                self.__log_verification(
                    f"Limit {fieldname} exceeded: {demand_value} > {limit_value}"
                )
                failed = fieldname
                result = False
        if result is True:
            self.__log_verification("Check OK")
        else:
            self.__log_verification(f"Check Failed : {failed}")

        return result

    async def __verify_limit(self, demand: int, limit: int):
        result = False
        if limit == -1:
            result = True
        elif limit >= demand:
            result = True
        return result

    def __log_verification(self, msg: str):
        if self.config.log_verification:
            self._log_info(msg)
