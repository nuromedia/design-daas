"""
Host information
"""

from dataclasses import dataclass
from app.daas.common.model import DaasObject
from app.daas.db.database import Database
from app.daas.objects.object_instance import InstanceObject
from app.qweb.logging.logging import LogTarget, Loggable


@dataclass
class ObjectRessources:
    """Contains available object ressources information"""

    objects: int
    instances: int
    object_vms: int
    object_images: int
    instance_vms: int
    instance_images: int
    max_cpus: int
    max_memory: int
    max_diskspace: int
    utilized_cpus: int
    utilized_memory: int
    utilized_diskspace: int

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__qualname__}("
            f"objects={self.objects},"
            f"vms={self.object_vms},"
            f"container={self.object_images}"
            ")"
        )


class Objectinfo(Loggable):
    """
    Keeps track of available host ressources
    """

    def __init__(self):
        Loggable.__init__(self, LogTarget.SYS)
        self.dbase = Database()

    async def initialize(self):
        """Initializes component"""
        await self.dbase.connect()
        self._log_info("ObjectInfo tool initialized")

    async def get_objectinfo_system(self) -> ObjectRessources:
        """Returns currently available host ressources"""
        return await self.__read_object_ressources(0)

    async def get_objectinfo_user(self, userid: int) -> ObjectRessources:
        """Returns currently available host ressources"""
        return await self.__read_object_ressources(userid)

    async def __read_object_ressources(self, userid: int = 0) -> ObjectRessources:
        """Returns currently available host ressources"""

        if userid != 0:
            objlist: list[DaasObject] = await self.dbase.get_daas_objects_by_owner(
                userid
            )
        else:
            objlist: list[DaasObject] = await self.dbase.all_daas_objects()
        instlist: list[InstanceObject] = await self.dbase.get_instances_by_owner(userid)

        objects = len(objlist)
        instances = len(instlist)
        object_vms = sum(1 for obj in objlist if obj.object_type == "vm")
        object_images = sum(1 for obj in objlist if obj.object_type == "container")
        instance_vms = sum(1 for inst in instlist if inst.app.object_type == "vm")
        instance_images = sum(
            1 for inst in instlist if inst.app.object_type == "container"
        )
        max_cpus = sum(obj.hw_cpus for obj in objlist)
        max_mem = sum(obj.hw_memory for obj in objlist)
        max_dsk = sum(obj.hw_disksize for obj in objlist)
        utilized_cpus = sum(inst.app.hw_cpus for inst in instlist)
        utilized_mem = sum(inst.app.hw_memory for inst in instlist)
        utilized_dsk = sum(inst.app.hw_disksize for inst in instlist)
        return ObjectRessources(
            objects,
            instances,
            object_vms,
            object_images,
            instance_vms,
            instance_images,
            max_cpus,
            max_mem,
            max_dsk,
            utilized_cpus,
            utilized_mem,
            utilized_dsk,
        )
