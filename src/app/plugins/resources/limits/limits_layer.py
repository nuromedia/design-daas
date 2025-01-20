"""Layer for resource limits"""

from dataclasses import asdict
from enum import Enum
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.common.model import DaaSEntity
from app.daas.db.database import Database
from app.daas.resources.limits.ressource_limits import RessourceLimits
from app.plugins.resources.limits.limits_tasks import LimitTask
from app.qweb.service.service_context import LayerObject, QwebObjectLayer
from app.qweb.common.qweb_tools import get_backend_component


class LimitObject(Enum):
    """Resource limit objects"""

    BYOWNER = "byowner"
    LIST = "list"


# pylint: disable=too-few-public-methods
class LimitObjectLayer(QwebObjectLayer):
    """Layer for resource limits"""

    async def get_object(
        self, obj: LayerObject, args: dict
    ) -> Optional[DaaSEntity | list]:
        """Retrieves entity from limit backend"""
        result = None
        db = Database()
        await db.connect()
        limiter = await get_backend_component(BackendName.LIMITS, RessourceLimits)
        if obj.objtype == LimitObject.BYOWNER.value:
            ownerid = args["id_owner"]
            result = await limiter.get_user_limit(ownerid)
            # self._log_info(f"fetched limit: {result}")
        elif obj.objtype == LimitObject.LIST.value:
            result = await limiter.list_user_limits()
            # self._log_info(f"fetched limits: {result}")
            return [asdict(x) for x in result]
        if result is not None:
            self.objects_returned += 1
        return result
