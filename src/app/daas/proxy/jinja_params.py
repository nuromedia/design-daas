from dataclasses import dataclass

from app.daas.common.enums import BackendName
from app.daas.objects.object_instance import InstanceObject
from app.daas.proxy.config import ViewerConfig
from app.plugins.platform.proxy.proxy_backend import ProxyBackend
from app.qweb.common.qweb_tools import get_backend
from app.qweb.logging.logging import LoggerConfig
from app.qweb.service.service_runtime import get_qweb_runtime


@dataclass
class JinjaParamsInstance:
    """Instance parameters to be passed to the viewer"""

    instance: str
    owner: int
    token: str
    backend_url: str
    tunnel_url: str
    referrer: str
    contype: str
    resolution: str
    resize: str
    scale: str
    dpi: int
    colors: int
    force_lossless: bool
    is_vm: int
    is_windows: int


@dataclass
class JinjaParamsViewer:
    """Viewer parameters to be passed to the viewer"""

    log_enabled: int
    log_resize: int
    log_summary: int
    log_tunnel: int
    log_client: int
    log_switcher: int
    log_watcher: int
    observer_ms: int
    fetch_ms: int
    check_ms: int
    reconnect_ms: int
    reconnect_default_ms: int
    reconnect_delayed_ms: int
    reconnect_max: int
    reconnect_enabled: int


async def get_jinja_params_viewer() -> JinjaParamsViewer:
    """Create Jinja params for the viewer"""
    runtime = get_qweb_runtime()
    proxy = await get_backend(BackendName.PROXY, ProxyBackend)
    cfg_log: LoggerConfig = runtime.cfg_log
    cfg_viewer: ViewerConfig = proxy.cfg_proxy

    return JinjaParamsViewer(
        log_enabled=1 if cfg_log.log_web_enabled else 0,
        log_resize=1 if cfg_log.log_web_resize else 0,
        log_summary=1 if cfg_log.log_web_summary else 0,
        log_tunnel=1 if cfg_log.log_web_tunnel else 0,
        log_client=1 if cfg_log.log_web_client else 0,
        log_switcher=1 if cfg_log.log_web_switcher else 0,
        log_watcher=1 if cfg_log.log_web_watcher else 0,
        fetch_ms=cfg_viewer.fetch_ms,
        check_ms=cfg_viewer.check_ms,
        reconnect_ms=cfg_viewer.reconnect_min_ms,
        observer_ms=cfg_viewer.observer_ms,
        reconnect_default_ms=cfg_viewer.reconnect_default_ms,
        reconnect_delayed_ms=cfg_viewer.reconnect_delayed_ms,
        reconnect_max=cfg_viewer.reconnect_max,
        reconnect_enabled=1 if cfg_viewer.reconnect_enabled else 0,
    )


async def get_jinja_params_instance(
    instance: InstanceObject, token: str, referrer: str = ""
) -> JinjaParamsInstance:
    """Create Jinja params for the instance"""
    proxy = await get_backend(BackendName.PROXY, ProxyBackend)
    cfg_viewer: ViewerConfig = proxy.cfg_proxy
    ref = referrer
    id_inst = instance.id
    hostproto = cfg_viewer.viewer_protocol
    hostip = cfg_viewer.viewer_host
    hostport = f"{cfg_viewer.viewer_port}"
    backend_url = f"{hostproto}://{hostip}:{hostport}"
    viewer_url = f"wss://{hostip}:{hostport}/wss/connect"
    tunnel_url = f"{viewer_url}/{id_inst}/{token}"

    return JinjaParamsInstance(
        instance=instance.id,
        owner=instance.app.id_owner,
        token=token,
        backend_url=backend_url,
        tunnel_url=tunnel_url,
        referrer=ref,
        contype=f"{instance.app.viewer_contype}",
        resolution=f"{instance.app.viewer_resolution}",
        resize=f"{instance.app.viewer_resize}",
        scale=f"{instance.app.viewer_scale}",
        dpi=instance.app.viewer_dpi,
        colors=instance.app.viewer_colors,
        force_lossless=instance.app.viewer_force_lossless,
        is_vm=1 if instance.app.object_type == "vm" else 0,
        is_windows=1 if instance.app.os_type in ("win10", "win11") else 0,
    )
