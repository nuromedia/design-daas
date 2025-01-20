"""
Docker facade
"""

import time
import os
import json
import ast
from dataclasses import dataclass
from typing import Iterator, Optional
import docker
import docker.errors
import docker.models
from docker.models.containers import Container
from docker.models.images import Image

from app.qweb.logging.logging import LogTarget, Loggable
from app.qweb.service.service_runtime import get_qweb_runtime


@dataclass
class DockerImageInfo:
    """
    A info object for Docker images
    """

    name: str
    attrs: dict
    tag: str


@dataclass
class DockerServicesConfig:
    service_containers: list[list]


@dataclass
class ContainerConfigDocker:
    image: str
    name: str
    privileged: bool
    bind_ports: list[str]
    volumes: list[str]
    cpus: int
    memory: int


@dataclass
class DockerContainerInfo:
    """
    A info object for Docker container
    """

    name: str
    id_container: str
    status: str
    info_image: DockerImageInfo
    stats_raw: dict
    stats_cpu: dict
    stats_mem: dict
    stats_disk: dict
    stats_net: dict


@dataclass
class DockerRequestConfig:
    """A configuration for the DockerRequest component"""

    host: str
    wait_services_ms: int
    logrequest: bool


class DockerRequest(Loggable):
    """A component to wrap various docker commands"""

    def __init__(
        self,
        cfg: DockerRequestConfig,
        cfg_services: DockerServicesConfig,
    ):
        Loggable.__init__(self, LogTarget.CONTAINER)
        self.config = cfg
        self.config_services = cfg_services
        self.docker = self.__connect()

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"(host={self.config.host},"
            f"logrequest={self.config.logrequest})"
        )

    async def connect(self):
        """Connects the component"""
        self.docker = self.__connect()
        if self.docker is not None:
            services = self._read_service_config()
            for svc in services:
                await self.docker_service_start(svc)
            if self.config.wait_services_ms > 0:
                self._log_info(
                    f"Waiting {self.config.wait_services_ms}ms for started services"
                )
                time.sleep(self.config.wait_services_ms / 1000)
            self.connected = True
        return self.connected

    async def disconnect(self) -> bool:
        """Disconnects the component"""
        if self.docker is not None:
            services = self._read_service_config()
            self._log_info(f"Stopping {len(services)} services:")
            for svc in services:
                self._log_info(f"Stopping {svc.name}")
                await self.docker_service_stop(svc)
        self.docker = None
        self.connected = False
        return True

    async def docker_image_build(
        self, dockerfile: str, tag: str
    ) -> tuple[int, str, str]:
        """Build image"""
        if self.docker is None:
            return 1, "", "No docker env"
        if os.path.exists(dockerfile) is False:
            return 2, "", f"File is not present: '{dockerfile}'"
        path = os.path.dirname(dockerfile)

        str_out = ""
        try:
            image, build_log = self.docker.images.build(
                path=path.lower(),
                dockerfile=dockerfile,
                tag=tag,
                rm=True,
                forcerm=True,
            )
            if image is None:
                return 2, "", "Image was not created"

            str_out = self._read_docker_log(build_log)
        except Exception as exe:
            self._log_error("Exception on image build:", 3, exe)
            return 3, "", "Error on build"
        return 0, str_out, ""

    def _read_docker_log(self, build_log: Iterator) -> str:
        lines = []
        for log in build_log:
            if isinstance(log, (bytes, bytearray)):
                log_decoded = log.decode("utf-8")
                log_entry = json.loads(log_decoded)
            else:
                logstr = log.__str__()  # .replace("'", '"')
                log_sanitized = ast.literal_eval(logstr)
                # Convert the object to a properly formatted JSON string
                log_entry = json.loads(json.dumps(log_sanitized))

            if "stream" in log_entry:
                lines.append(log_entry["stream"])
        return "\n".join(lines)

    async def docker_image_list(self, detailed: bool = False) -> list[DockerImageInfo]:
        """
        Lists all docker images
        """
        result: list[DockerImageInfo] = []
        if self.docker is None:
            return result
        imglist = self.docker.images.list()
        for image in imglist:
            infos = self.__create_image_info(image, detailed)
            for single in infos:
                result.append(single)
        return result

    async def docker_image_delete(self, tag: str = "") -> tuple:
        """
        Deletes docker images
        """
        result = 1, "", "Unknown error"
        if self.docker is None:
            return result
        try:
            self.docker.images.remove(image=tag, force=True)
            result = 0, "", ""
        except docker.errors.ImageNotFound:
            result = 1, "", "Image not found"
        return result

    async def docker_service_start(self, cfg: ContainerConfigDocker) -> tuple:
        """
        Starts a new service container based on specified image
        """
        if self.docker is None:
            return 1, "", "No docker env"
        container_config = self._create_run_config(
            cfg.image,
            cfg.name,
            cfg.cpus,
            cfg.memory,
            cfg.privileged,
            cfg.bind_ports,
            cfg.volumes,
        )
        try:
            await self.docker_container_stop(cfg.name, True)
            self._log_info(f"Running service: {cfg.name}")
            container = self.docker.containers.run(**container_config)
            if container is not None:
                name = container.name
                image = container.image
                self._log_info(f"Started service {name} from {image}")
                return 0, name, ""
        except Exception as exe:
            self._log_error(f"  1 -> Exception raised1: {exe}")
        return 1, "", "Service was not created!"

    async def docker_service_stop(self, cfg: ContainerConfigDocker) -> tuple:
        """Stops a service container"""
        if self.docker is None:
            return 1, "", "No docker env"
        try:
            await self.docker_container_stop(cfg.name, True)
            self._log_info(f"Stopped service {cfg.name} from {cfg.image}")
            return 0, "", ""
        except Exception as exe:
            self._log_error(f"  1 -> Exception raised1: {exe}")
        return 1, "", "Service was not stopped!"

    async def docker_container_start(
        self,
        image: str,
        name: str,
        cpus: int,
        memory_b: int,
        privileged: bool = False,
        ports: list[str] = [],
        volumes: list[str] = [],
    ) -> tuple:
        """
        Starts a new container based on specified image
        """
        if self.docker is None:
            return 1, "", "No docker env"
        container_config = self._create_run_config(
            image, name, cpus, memory_b, privileged, ports, volumes
        )
        try:
            await self.docker_container_stop(name, True)
            container = self.docker.containers.run(**container_config)
            if container is not None:
                name = container.name
                image = container.image
                self._log_info(f"Started container {name} from {image}")
                return 0, name, ""
        except Exception as exe:
            self._log_error(f"  1 -> Exception raised1: {exe}")
        return 1, "", "Container was not created!"

    async def docker_container_stop(self, name: str, force: bool) -> tuple:
        """
        Starts a new container based on specified image
        """
        if self.docker is None:
            return 1, "", "No docker env"
        container = None
        contlist = self.docker.containers.list()
        for cont in contlist:
            if name == cont.name:
                container = self.docker.containers.get(container_id=cont.name)
                try:
                    if container is not None:
                        if force:
                            container.kill()
                            self._log_info(f"Killed {container.short_id}")
                        else:
                            container.stop()
                            self._log_info(f"Stopped {container.short_id}")
                        while await self.docker_container_get(name) is not None:
                            time.sleep(0.1)
                        return 0, name, ""
                except Exception as exe:
                    self._log_error(f"  1 -> Exception raised2: {exe}")
        return 2, "", "No container"

    async def docker_get_container_ip(self, container_id: str) -> str:
        """
        Obtain an IP address for the given container.

        Can fail e.g. if the container doesn't exist
        or has no IP addresses.
        Doesn't guarantee that the IP address will be routable.
        """
        if self.docker is None:
            return ""
        inspect = self.docker.api.inspect_container(container_id)

        addresses = [
            net["IPAddress"] for net in inspect["NetworkSettings"]["Networks"].values()
        ]

        assert addresses, f"container {container_id} must have at least one IP address"

        # if there are multiple IPs, log them all and return the first
        if len(addresses) > 1:
            self._log_info(f"container {container_id} has multiple IPs: {addresses}")
        return addresses[0]

    async def docker_container_list(
        self, include_stats: bool = False
    ) -> list[DockerContainerInfo]:
        """
        List containers
        """
        result: list[DockerContainerInfo] = []
        if self.docker is None:
            return result
        contlist = self.docker.containers.list()
        for cont in contlist:
            info = self.__create_container_info(cont, include_stats)
            result.append(info)
        return result

    async def docker_container_logs(self, name: str) -> tuple[int, str, str]:
        """
        Container logs
        """
        container = await self.docker_container_get(name)
        if container is not None:
            return 0, f"{container.logs()}", ""
        code = 1
        msg = f"No container with specified name: {name}"
        self._log_error(msg)
        return (code, "", msg)

    # pylint: disable=broad-exception-caught
    async def docker_container_get(self, name: str) -> Optional[Container]:
        """Returns container specified by name"""
        result = None
        if self.docker is None:
            return result
        try:
            result = self.docker.containers.get(name)
        except docker.errors.NotFound:
            result = None
        return result

    def _read_service_config(self) -> list[ContainerConfigDocker]:
        result = []
        for service in self.config_services.service_containers:
            if isinstance(service, list):
                if len(service) == 5:
                    opts = service[2]
                    priv = False
                    ports = []
                    volumes = []
                    for opt in opts:
                        if opt.startswith("--privileged"):
                            priv = True
                        if opt.startswith("-p"):
                            ports.append(opt)
                        elif opt.startswith("-v"):
                            volumes.append(opt)

                    cfg = ContainerConfigDocker(
                        image=service[0],
                        name=service[1],
                        privileged=priv,
                        bind_ports=ports,
                        volumes=volumes,
                        cpus=service[3],
                        memory=service[4],
                    )
                    result.append(cfg)
        return result

    def _create_run_config(
        self,
        image: str,
        name: str,
        cpus: int,
        memory_b: int,
        privileged: bool = False,
        ports: list[str] = [],
        volumes: list[str] = [],
    ) -> dict:

        mapped_ports = self._get_config_ports(ports)
        mapped_volumes = self._get_config_volumes(volumes)
        return {
            "name": name,
            "image": image,
            "detach": True,
            "remove": True,
            "privileged": privileged,
            "ports": mapped_ports,
            "volumes": mapped_volumes,
            "devices": ["/dev/rtc:/dev/rtc"],
            "cpuset_cpus": "0-7",
            "cpu_quota": cpus * 100000,
            "cpu_period": 1 * 100000,
            "mem_limit": f"{memory_b /1024**2}m",
        }

    def _get_config_ports(self, ports: list[str]) -> dict:
        mapped_ports = {}
        for opt in ports:
            arr = opt.split(" ")
            if len(arr) == 2:
                portopt = arr[1]
                portargs = portopt.split(":")
                if len(portargs) == 3:
                    host = portargs[0]
                    hostport = portargs[1]
                    cntport = portargs[2]
                    mapped_ports[cntport] = (host, hostport)
        return mapped_ports

    def _get_config_volumes(self, volumes: list[str]) -> dict:
        mapped_volumes = {}
        runtime = get_qweb_runtime()
        for opt in volumes:
            arr = opt.split(" ")
            if len(arr) == 2:
                volopt = arr[1]
                volargs = volopt.split(":")
                if len(volargs) == 3:
                    hostpath = volargs[0]
                    if hostpath.startswith("/") is False:
                        hostpath = (
                            f"{runtime.cfg_qweb.sys.root_path}/"
                            f"{runtime.cfg_qweb.sys.data_path}/"
                            f"{hostpath}"
                        )
                    cntpath = volargs[1]
                    permissions = volargs[2]
                    mapped_volumes[hostpath] = {"bind": cntpath, "mode": permissions}
        return mapped_volumes

    # pylint: disable=broad-exception-caught
    def __docker_image_get(self, tag: str) -> Optional[Image]:
        result = None
        if self.docker is None:
            return result
        try:
            result = self.docker.images.get(tag)
        except docker.errors.ImageNotFound:
            result = None
        return result

    def __create_image_info(
        self, image: Image, detailed: bool = False
    ) -> list[DockerImageInfo]:
        ret: list[DockerImageInfo] = []
        for tag in image.tags:
            name = tag
            if ":" in tag:
                name = tag.split(":")[0]
            result = DockerImageInfo(name, image.attrs, tag)
            ret.append(result)

        return ret

    def __create_container_info(
        self, cont, detailed: bool = False
    ) -> DockerContainerInfo:
        result = {}
        name = cont.name
        status = cont.status
        stats_raw = {}
        stats_cpu = {}
        stats_mem = {}
        stats_disk = {}
        stats_net = {}
        imginfo = DockerImageInfo(name, cont.image.attrs, cont.image.tags)
        if detailed is True:
            stats_raw = cont.stats(stream=False)
            stats_cpu = stats_raw["cpu_stats"]
            stats_mem = stats_raw["memory_stats"]
            stats_disk = stats_raw["blkio_stats"]
            stats_net = stats_raw["networks"]
        result = DockerContainerInfo(
            name,
            cont.id,
            status,
            imginfo,
            stats_raw,
            stats_cpu,
            stats_mem,
            stats_disk,
            stats_net,
        )
        return result

    def __connect(self):
        return docker.from_env()

    async def docker_get_daemoninfo(self) -> str:
        """Returns info() output from currently used docker instance"""
        if self.docker is not None:
            return self.docker.info()
        return "No docker env"

    async def docker_image_inspect(self, tag: str) -> dict:
        """Inspect image"""
        image = self.__docker_image_get(tag)
        if image is not None:
            return image.attrs
        return {}
