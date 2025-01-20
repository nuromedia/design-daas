"""System information for objects"""

import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional
from app.daas.common.enums import BackendName
from app.daas.container.docker.DockerRequest import DockerContainerInfo, DockerRequest
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.qweb.common.qweb_tools import get_backend_component


class PersistanceStrategy(Enum):
    """Strategy for object persistance"""

    IGNORE = 1
    PERSIST = 2


class StatisticType(Enum):
    """Object statistics type"""

    VM_BOTH = 1
    VM_ON = 2
    VM_OFF = 3
    IMG_BOTH = 4
    IMG_ON = 5
    IMG_OFF = 6
    ALL_BOTH = 7
    ALL_ON = 8
    ALL_OFF = 9


# pylint: disable=too-many-instance-attributes
@dataclass
class SystemInfoProxmoxMachine:
    """Info Object for proxmox vms"""

    full_state_info: dict
    name: str
    id_object: str
    running: bool
    cpus: int
    mem_use: int
    mem_max: int
    disk_size: int
    disk_in: int
    disk_out: int
    net_in: int
    net_out: int
    template: bool


# pylint: disable=too-many-instance-attributes
@dataclass
class SystemInfoDockerContainer:
    """Info Object for docker container"""

    full_state_info: dict
    name: str
    id_object: str
    running: bool
    cpus: int
    mem_usage: int
    mem_limit: int
    disk_in: int
    disk_out: int
    net_in: int
    net_out: int


# pylint: disable=too-many-instance-attributes
@dataclass
class SystemInfoDockerImage:
    """Info Object for docker images"""

    full_state_info: dict
    name: str
    id_object: str
    tag: str
    running: bool
    containers: list[SystemInfoDockerContainer]
    container_amount: int
    attributes: dict
    running: bool
    cpus: int
    mem_usage: int
    mem_limit: int
    disk_size: int
    disk_in: int
    disk_out: int
    net_in: int
    net_out: int
    template: bool


@dataclass
class SystemInfoObjectUtilization:
    """Statistics Object for object monitoring"""

    # statistics_type: StatisticType
    amount: int
    cpus: int
    mem_use: int
    mem_max: int
    disk_size: int
    disk_in: int
    disk_out: int
    net_in: int
    net_out: int

    def tostring(self) -> str:
        """Converts to short form"""
        conv_mb = 1024 * 1024
        conv_gb = conv_mb * 1024
        mem_use = self.mem_use / conv_gb
        mem_max = self.mem_max / conv_gb
        disksize = self.disk_size / conv_gb
        disk_in = self.disk_in / conv_mb
        disk_out = self.disk_out / conv_mb
        net_in = self.net_in / conv_mb
        net_out = self.net_out / conv_mb
        return (
            f"num: {self.amount:5} "
            f"cpu: {self.cpus:5} "
            f"mem: {mem_use:2.0f}/{mem_max:2.0f} GB "
            f"dsk_sz : {disksize:7.2f} GB "
            f"dsk_In : {disk_in:7.2f} MB "
            f"dsk_out: {disk_out:7.2f} MB "
            f"net_in : {net_in:7.2f} MB "
            f"net_out: {net_out:7.2f} MB"
        )


# pylint: disable=too-few-public-methods
class SystemInfoObjects:
    """Info Object for all stored objects"""

    vms_list: list[SystemInfoProxmoxMachine]
    image_list: list[SystemInfoDockerImage]
    vms_usage_total: SystemInfoObjectUtilization
    vms_usage_online: SystemInfoObjectUtilization
    vms_usage_offline: SystemInfoObjectUtilization
    images_usage_total: SystemInfoObjectUtilization
    images_usage_online: SystemInfoObjectUtilization
    images_usage_offline: SystemInfoObjectUtilization
    all_usage_total: SystemInfoObjectUtilization
    all_usage_online: SystemInfoObjectUtilization
    all_usage_offline: SystemInfoObjectUtilization

    def __init__(
        self,
        vms: list[SystemInfoProxmoxMachine],
        images: list[SystemInfoDockerImage],
    ):
        self.vms_list = vms
        self.image_list = images
        self.vms_usage_total = self.__sum_vms(vms, StatisticType.VM_BOTH)
        self.vms_usage_online = self.__sum_vms(vms, StatisticType.VM_ON)
        self.vms_usage_offline = self.__sum_vms(vms, StatisticType.VM_OFF)
        self.images_usage_total = self.__sum_images(images, StatisticType.IMG_BOTH)
        self.images_usage_online = self.__sum_images(images, StatisticType.IMG_ON)
        self.images_usage_offline = self.__sum_images(images, StatisticType.IMG_OFF)
        self.all_usage_total = self.__sum_all(StatisticType.ALL_BOTH)
        self.all_usage_online = self.__sum_all(StatisticType.ALL_ON)
        self.all_usage_offline = self.__sum_all(StatisticType.ALL_OFF)
        # for vm in self.vms_list:
        #     print(f"VMS: {vm.name} {vm.running}")
        # for img in self.image_list:
        #     print(f"IMG: {img.name} {img.running}")

        # print(f"VMS-OFF: {self.vms_usage_offline.tostring()}")
        # print(f"VMS-ON : {self.vms_usage_online.tostring()}")
        # print(f"VMS-TOT: {self.vms_usage_total.tostring()}")
        # print(f"IMG-OFF: {self.images_usage_offline.tostring()}")
        # print(f"IMG-ON : {self.images_usage_online.tostring()}")
        # print(f"IMG-TOT: {self.images_usage_total.tostring()}")
        # print(f"ALL-OFF: {self.all_usage_offline.tostring()}")
        # print(f"ALL-ON : {self.all_usage_online.tostring()}")
        # print(f"ALL-TOT: {self.all_usage_total.tostring()}")

    def tojson(self):
        """Converts to json object"""
        return {
            # "self.vms_list": self.vms_list,
            # "self.image_list": self.image_list,
            "self.vms_usage_total": asdict(self.vms_usage_total),
            "self.vms_usage_online": asdict(self.vms_usage_online),
            "self.vms_usage_offline": asdict(self.vms_usage_offline),
            "self.images_usage_total": asdict(self.images_usage_total),
            "self.images_usage_online": asdict(self.images_usage_online),
            "self.images_usage_offline": asdict(self.images_usage_offline),
            "self.all_usage_total": asdict(self.all_usage_total),
            "self.all_usage_online": asdict(self.all_usage_online),
            "self.all_usage_offline": asdict(self.all_usage_offline),
        }

    def __sum_all(self, stats_type: StatisticType):
        usage_vms = self.vms_usage_total
        usage_img = self.images_usage_total
        if stats_type == StatisticType.ALL_BOTH:
            usage_vms = self.vms_usage_total
            usage_img = self.images_usage_total
        elif stats_type == StatisticType.ALL_ON:
            usage_vms = self.vms_usage_online
            usage_img = self.images_usage_online
        elif stats_type == StatisticType.ALL_OFF:
            usage_vms = self.vms_usage_offline
            usage_img = self.images_usage_offline

        return SystemInfoObjectUtilization(
            usage_img.amount + usage_vms.amount,
            usage_img.cpus + usage_vms.cpus,
            usage_img.mem_use + usage_vms.mem_use,
            usage_img.mem_max + usage_vms.mem_max,
            usage_img.disk_size + usage_vms.disk_size,
            usage_img.disk_in + usage_vms.disk_in,
            usage_img.disk_out + usage_vms.disk_out,
            usage_img.net_in + usage_vms.net_in,
            usage_img.net_out + usage_vms.net_out,
        )

    def __sum_images(
        self,
        object_list: list[SystemInfoDockerImage],
        stats_type: StatisticType,
    ) -> SystemInfoObjectUtilization:

        amount: int = 0
        cpus: int = 0
        mem_use: int = 0
        mem_max: int = 0
        disk_size: int = 0
        disk_in: int = 0
        disk_out: int = 0
        net_in: int = 0
        net_out: int = 0
        templates: int = 0

        for info in object_list:
            if (
                (stats_type == StatisticType.IMG_BOTH)
                or (stats_type == StatisticType.IMG_ON and info.running is True)
                or (stats_type == StatisticType.IMG_OFF and info.running is False)
            ):
                templates += 1 if info.template is True else 0
                amount += 1
                cpus += info.cpus
                mem_use += info.mem_usage
                mem_max += info.mem_limit
                disk_size += info.disk_size
                disk_in += info.disk_in
                disk_out += info.disk_out
                net_in += info.net_in
                net_out += info.net_out
        return SystemInfoObjectUtilization(
            amount,
            cpus,
            mem_use,
            mem_max,
            disk_size,
            disk_in,
            disk_out,
            net_in,
            net_out,
        )

    def __sum_vms(
        self,
        object_list: list[SystemInfoProxmoxMachine],
        stats_type: StatisticType,
    ) -> SystemInfoObjectUtilization:

        amount: int = 0
        cpus: int = 0
        mem_use: int = 0
        mem_max: int = 0
        disk_size: int = 0
        disk_in: int = 0
        disk_out: int = 0
        net_in: int = 0
        net_out: int = 0
        templates: int = 0

        for info in object_list:
            if (
                (stats_type == StatisticType.VM_BOTH)
                or (stats_type == StatisticType.VM_ON and info.running is True)
                or (stats_type == StatisticType.VM_OFF and info.running is False)
            ):
                amount += 1
                templates += 1 if info.template is True else 0
                disk_size += info.disk_size
                if info.running:
                    cpus += info.cpus
                    mem_use += info.mem_use
                    mem_max += info.mem_use
                    disk_in += info.disk_in
                    disk_out += info.disk_out
                    net_in += info.net_in
                    net_out += info.net_out
        return SystemInfoObjectUtilization(
            amount,
            cpus,
            mem_use,
            mem_max,
            disk_size,
            disk_in,
            disk_out,
            net_in,
            net_out,
        )


class ObjectStats:
    """
    Info tool for objects
    """

    def __init__(self):
        self.logger = logging.getLogger("")
        self.last_info: Optional[SystemInfoObjects] = None

    async def create_object_info(self, detailed: bool) -> SystemInfoObjects:
        """Enumerates obejcts"""
        vms = await self.enumerate_vms(detailed)
        images = await self.enumerate_docker_objects(detailed)
        self.last_info = SystemInfoObjects(vms, images)
        return self.last_info

    async def enumerate_vms(
        self,
        detailed: bool,
    ) -> list[SystemInfoProxmoxMachine]:
        """Enumerates all proxmox objects"""

        api = await get_backend_component(BackendName.VM, ApiProxmox)
        cfg = api.config_prox
        result: list[SystemInfoProxmoxMachine] = []

        # Obtain backend data
        response, data = await api.prox_vmlist(cfg.node)
        if response is not None and response.status == 200 and "data" in data:
            vmlist = data["data"]
            for sysobject in vmlist:
                if "vmid" in sysobject and "name" in sysobject:
                    vmid: str = sysobject["vmid"]
                    name: str = sysobject["name"]
                    running: bool = sysobject["status"] != "stopped"
                    template: bool = False
                    if "template" in sysobject:
                        template = True
                    cpus = int(sysobject["cpus"])
                    mem_use = int(sysobject["maxmem"])
                    mem_max = int(sysobject["maxmem"])
                    disk_size = int(sysobject["maxdisk"])
                    disk_in = int(sysobject["diskread"])
                    disk_out = int(sysobject["diskwrite"])
                    net_in = int(sysobject["netin"])
                    net_out = int(sysobject["netout"])
                    info = SystemInfoProxmoxMachine(
                        sysobject,
                        name,
                        vmid,
                        running,
                        cpus,
                        mem_use,
                        mem_max,
                        disk_size,
                        disk_in,
                        disk_out,
                        net_in,
                        net_out,
                        template,
                    )
                    result.append(info)
        return result

    async def enumerate_docker_objects(
        self, detailed: bool
    ) -> list[SystemInfoDockerImage]:
        """Enumerates all docker objects"""

        container = await self.enumerate_container(detailed)
        return await self.enumerate_images(container, detailed)

    # pylint: disable=too-many-locals
    async def enumerate_container(
        self, detailed: bool
    ) -> list[SystemInfoDockerContainer]:
        """Enumerates container objects"""
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        result: list[SystemInfoDockerContainer] = []
        conlist: list[DockerContainerInfo] = await api.docker_container_list(detailed)
        for sysobject in conlist:
            cpuinfo = sysobject.stats_cpu
            meminfo = sysobject.stats_mem
            diskinfo = sysobject.stats_disk
            netinfo = sysobject.stats_net
            cpus: int = 0
            mem_usage: int = 0
            mem_limit: int = 0
            disk_in: int = 0
            disk_out: int = 0
            net_in: int = 0
            net_out: int = 0
            if "online_cpus" in cpuinfo:
                cpus = 2  # int(cpuinfo["online_cpus"])
            if "usage" in meminfo and "limit" in meminfo:
                mem_usage = int(meminfo["usage"])
                mem_limit = int(meminfo["limit"])
            if "io_service_bytes_recursive" in diskinfo:
                iobytes = diskinfo["io_service_bytes_recursive"]
                if iobytes is not None and len(iobytes) >= 2:
                    disk_in = int(iobytes[0]["value"])
                    disk_out = int(iobytes[1]["value"])
            if "eth0" in netinfo:
                adapter = netinfo["eth0"]
                if "tx_bytes" in adapter and "rx_bytes" in adapter:
                    net_in = int(adapter["rx_bytes"])
                    net_out = int(adapter["tx_bytes"])
            info = SystemInfoDockerContainer(
                sysobject.stats_raw,
                sysobject.name,
                sysobject.id_container,
                (sysobject.status == "running"),
                cpus,
                mem_usage,
                mem_limit,
                disk_in,
                disk_out,
                net_in,
                net_out,
            )
            result.append(info)
        return result

    async def enumerate_images(
        self, container: list[SystemInfoDockerContainer], detailed: bool
    ) -> list[SystemInfoDockerImage]:
        """Enumerates image objects"""
        api = await get_backend_component(BackendName.CONTAINER, DockerRequest)
        result: list[SystemInfoDockerImage] = []
        imglist = await api.docker_image_list(detailed)
        if len(imglist) > 0:
            for sysobject in imglist:
                cpus: int = 0
                mem_usage: int = 0
                mem_limit: int = 0
                disk_size: int = 0
                disk_in: int = 0
                disk_out: int = 0
                net_in: int = 0
                net_out: int = 0
                matched: list[SystemInfoDockerContainer] = []
                name = sysobject.name
                dockerid = sysobject.attrs["Id"]
                disk_size = int(sysobject.attrs["Size"])
                template: bool = False
                for cont in container:
                    if cont.name == name:
                        matched.append(cont)
                        # print(f"Matched: {cont.name} - {name}")
                    # else:
                    #     print(f"Unmatched: {cont.name} - {name}")
                running: bool = len(matched) > 0
                if running is True:
                    cont = container[0]
                    cpus = cont.cpus
                    mem_usage = cont.mem_usage
                    mem_limit = cont.mem_limit
                    disk_in = cont.disk_in
                    disk_out = cont.disk_out
                    net_in = cont.net_in
                    net_out = cont.net_out
                    matched.append(cont)

                info = SystemInfoDockerImage(
                    asdict(sysobject),
                    name,
                    dockerid,
                    sysobject.tag,
                    running,
                    matched,
                    len(matched),
                    sysobject.attrs,
                    cpus,
                    mem_usage,
                    mem_limit,
                    disk_size,
                    disk_in,
                    disk_out,
                    net_in,
                    net_out,
                    template,
                )
                result.append(info)

        return result

    def __log_info(self, msg: str):
        self.logger.info("%s", msg)
