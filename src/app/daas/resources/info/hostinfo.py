"""
Host information
"""

import subprocess
from dataclasses import dataclass
import os
import logging
from typing import Optional
import psutil

from app.daas.common.enums import BackendName
from app.daas.storage.cephstore import Cephstore
from app.daas.storage.filestore import Filestore
from app.daas.vm.proxmox.ProxmoxApi import ApiProxmox
from app.plugins.platform.vm.vm_backend import VmBackend
from app.plugins.storage.ceph.ceph_backend import CephBackend
from app.plugins.storage.files.file_backend import FileBackend
from app.qweb.service.service_runtime import get_qweb_runtime


# pylint:disable=too-many-instance-attributes
@dataclass
class HostRessources:
    """Contains available host ressources information"""

    max_cpus: int
    max_memory: int
    max_disk_space_data: int
    max_disk_space_ceph: int
    max_disk_space_iso: int
    max_disk_space_images: int
    utilized_cpus: float
    utilized_memory: int
    utilized_disk_space_data: int
    utilized_disk_space_ceph: int
    utilized_disk_space_iso: int
    utilized_disk_space_images: int


# pylint:disable=too-many-instance-attributes
@dataclass
class PathSize:
    """Sizeinfo for a path"""

    path: str
    exists: bool
    device: str
    mountdir: str
    path_size: int
    partition_size: int
    partition_used: int
    partition_free: int


class Hostinfo:
    """
    Keeps track of available host ressources
    """

    def __init__(self):
        self.logger = logging.getLogger("daas.backend")

    async def read_host_ressources(self) -> Optional[HostRessources]:
        """Returns currently available host ressources"""
        cpu_total = self.__read_host_cpus()
        cpu_used = self.__read_host_cpu_utilization()
        mem_total = self.__read_host_memory_total()
        mem_used = self.__read_host_memory_used()
        diskinfo_local = await self.__read_host_disksize_local()
        diskinfo_ceph = await self.__read_host_disksize_ceph()
        diskinfo_iso = await self.__read_host_disksize_iso()
        diskinfo_img = await self.__read_host_disksize_images()
        if (
            diskinfo_local is not None
            and diskinfo_ceph is not None
            and diskinfo_iso is not None
            and diskinfo_img is not None
        ):
            return HostRessources(
                cpu_total,
                mem_total,
                diskinfo_local.partition_size,
                diskinfo_ceph.partition_size,
                diskinfo_iso.partition_size,
                diskinfo_img.partition_size,
                cpu_used,
                mem_used,
                diskinfo_local.partition_used,
                diskinfo_ceph.partition_used,
                diskinfo_iso.partition_used,
                diskinfo_img.partition_used,
            )
        return None

    def __read_host_cpus(self) -> int:
        """Returns currently available cpus"""
        count = os.cpu_count()
        if count is None:
            return 0
        return count

    # pylint:disable=import-outside-toplevel
    async def __read_host_disksize_ceph(self) -> Optional[PathSize]:
        """Returns current sizeinfo for local files"""

        filestore = await self._get_backend_ceph()
        fs_config = filestore.config
        # mnt = fs_config.daasfs.folder_mount
        mnt = fs_config.daasfs["folder_mount"]
        folder_pub = f"{mnt}/daasfs/"
        return await self.__get_diskinfo(folder_pub)

    async def _get_backend_ceph(self) -> Cephstore:
        runtime = get_qweb_runtime()
        backend = runtime.backends.get(BackendName.CEPH.value)
        assert backend is not None and isinstance(backend, CephBackend)
        return backend.component

    async def _get_backend_files(self) -> Filestore:
        runtime = get_qweb_runtime()
        backend = runtime.backends.get(BackendName.FILE.value)
        assert backend is not None and isinstance(backend, FileBackend)
        return backend.component

    async def _get_backend_vmconfig(self):
        runtime = get_qweb_runtime()
        backend = runtime.backends.get(BackendName.VM.value)
        assert backend is not None and isinstance(backend, VmBackend)
        return backend.component.config_prox

    # pylint:disable=import-outside-toplevel
    async def __read_host_disksize_iso(self) -> Optional[PathSize]:
        """Returns current sizeinfo for local iso images"""

        config = await self._get_backend_vmconfig()
        size_iso = await self.__get_diskinfo(
            f"{config.main_folder}/{config.storage_iso}"
        )
        if size_iso is not None:
            return PathSize(
                size_iso.path,
                True,
                size_iso.device,
                size_iso.mountdir,
                size_iso.path_size,
                size_iso.partition_size,
                size_iso.partition_used,
                size_iso.partition_free,
            )

    # pylint:disable=import-outside-toplevel
    async def __read_host_disksize_images(self) -> Optional[PathSize]:
        """Returns current sizeinfo for local vm images"""
        config = await self._get_backend_vmconfig()
        size_img = await self.__get_diskinfo(
            f"{config.main_folder}/{config.storage_img}"
        )
        if size_img is not None:
            return PathSize(
                size_img.path,
                True,
                size_img.device,
                size_img.mountdir,
                size_img.path_size,
                size_img.partition_size,
                size_img.partition_used,
                size_img.partition_free,
            )

    # pylint:disable=import-outside-toplevel
    async def __read_host_disksize_local(self) -> Optional[PathSize]:
        """Returns current sizeinfo for local files"""
        filestore = await self._get_backend_files()
        fs_config = filestore.config
        size_tmp = await self.__get_diskinfo(fs_config.folder_tmp)
        size_upload = await self.__get_diskinfo(fs_config.folder_upload)
        size_shared = await self.__get_diskinfo(fs_config.folder_shared)
        size_docker = await self.__get_diskinfo(fs_config.folder_docker)
        if (
            size_tmp is not None
            and size_upload is not None
            and size_shared is not None
            and size_docker is not None
        ):
            total_size = (
                size_tmp.path_size
                + size_shared.path_size
                + size_upload.path_size
                + size_docker.path_size
            )
            return PathSize(
                size_tmp.path,
                True,
                size_tmp.device,
                size_tmp.mountdir,
                total_size,
                size_tmp.partition_size,
                size_tmp.partition_used,
                size_tmp.partition_free,
            )

    def __read_host_cpu_utilization(self) -> float:
        """Returns currently utilization of cpu"""
        return psutil.cpu_percent(interval=0.1)

    def __read_host_memory_total(self) -> int:
        """Returns current total memory"""
        memory_info = psutil.virtual_memory()
        return memory_info.total

    def __read_host_memory_used(self) -> int:
        """Returns current total memory"""
        memory_info = psutil.virtual_memory()
        return memory_info.used

    async def __get_disk_usage(self, path: str) -> int:
        """Get used bytes for folder"""
        if os.path.exists(path):
            result = subprocess.run(["du", "-sb", path], stdout=subprocess.PIPE)
            ret = result.stdout
            if ret != "":
                arr = result.stdout.split()
                if len(arr) > 0:
                    return int(arr[0])
        return 0

    async def __get_diskinfo(self, path: str) -> PathSize:
        """Returns disk size"""
        if os.path.exists(path):
            total_used_space = await self.__get_disk_usage(path)
            result = subprocess.run(["df", "-B1", path], stdout=subprocess.PIPE)
            lines = result.stdout.decode("utf-8").splitlines()
            if len(lines) > 1:
                devname, total, used, available, _, mountdir = lines[1].split()
                return PathSize(
                    path,
                    True,
                    devname,
                    mountdir,
                    total_used_space,
                    int(total),
                    int(used),
                    int(available),
                )
        return PathSize(path, False, "", "", 0, 0, 0, 0)

    async def initialize(self):
        """Initializes component"""
        self.__log_info("Initialized")

    def __log_info(self, msg: str):
        self.logger.info("Hostinfo          : %s", msg)
