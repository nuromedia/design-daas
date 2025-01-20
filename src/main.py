"""Default app"""

import asyncio
import sys
from app.plugins.platform.extensions.extensions_plugin import ExtensionsPlugin
from app.plugins.resources.admin.admin_plugin import AdminPlugin
from app.qweb.common.config import QwebConfig
from app.qweb.service.service_runtime import get_qweb_runtime
from app.plugins.common.common import PluginCollection
from app.plugins.core.auth.auth_plugin import AuthPlugin
from app.plugins.core.db.db_plugin import DatabasePlugin
from app.plugins.core.task.task_plugin import TaskPlugin
from app.plugins.platform.container.container_plugin import ContainerPlugin
from app.plugins.platform.instances.inst_plugin import InstancePlugin
from app.plugins.platform.messaging.messaging_plugin import MessagingPlugin
from app.plugins.platform.node.node_plugin import NodePlugin
from app.plugins.platform.phases.phases_plugin import PhasesPlugin
from app.plugins.platform.proxy.proxy_plugin import ProxyPlugin
from app.plugins.platform.vm.vm_plugin import VmPlugin
from app.plugins.resources.info.info_plugin import InfoPlugin
from app.plugins.resources.limits.limits_plugin import LimitPlugin
from app.plugins.storage.ceph.ceph_plugin import CephPlugin
from app.plugins.storage.files.file_plugin import FilePlugin
from app.plugins.testing.test_plugin import TestPlugin


async def _load_plugins(cfg: QwebConfig) -> PluginCollection:
    col = PluginCollection(
        [
            AuthPlugin(),
            DatabasePlugin(),
            NodePlugin(),
            TestPlugin(),
            ContainerPlugin(),
            VmPlugin(),
            FilePlugin(),
            CephPlugin(),
            MessagingPlugin(),
            InfoPlugin(),
            LimitPlugin(),
            ProxyPlugin(),
            TaskPlugin(),
            PhasesPlugin(),
            InstancePlugin(),
            AdminPlugin(),
            ExtensionsPlugin(),
        ],
        cfg.handler.enable_testing,
    )
    print("--- REGISTER PLUGINS -------------")
    await col.register_plugins()
    print("--- START PLUGINS -------------")
    await col.start_plugins()
    return col


async def _run_blocking():
    print("--- INIT RUNTIME -----------------")
    runtime_qweb = get_qweb_runtime(qwebfile="config/qweb.toml")
    cfg = runtime_qweb.cfg_qweb
    print("--- INIT PLUGINS -----------------")
    await _load_plugins(cfg)
    print("--- START RUNTIME ----------------")
    await runtime_qweb.start()
    print("")
    print("--- STOPPING RUNTIME -------------")
    print("--- STOP BACKENDS ----------------")
    await runtime_qweb.stop_backends()
    print("--- STOP TASKS -------------------")
    await runtime_qweb.stop_tasks()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 1:
        print(f"ARGV: {len(argv)} {argv}")
    else:
        print("DEFAULT STARTUP")
    try:
        asyncio.run(_run_blocking())
    except Exception as exe:
        t = type(exe)
        print(f"Exception handler: {t.__module__}.{t.__qualname__}")
