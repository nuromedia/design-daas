""" Plugin collection """

from app.qweb.service.service_plugin import LoadOrder, PluginBase


class PluginCollection:
    plugins: list[PluginBase] = []
    plugins_testing: list[PluginBase] = []
    plugins_early: list[PluginBase] = []
    plugins_core: list[PluginBase] = []
    plugins_platform: list[PluginBase] = []
    plugins_storage: list[PluginBase] = []
    plugins_late: list[PluginBase] = []

    def __init__(self, plugins: list[PluginBase], cfg_testing: bool):
        self.plugins = plugins
        self.testing_enabled = cfg_testing
        self._init_plugins()

    async def register_plugins(self):
        for order in LoadOrder:
            await self._register_plugingroup(order)

    async def start_plugins(self):
        for order in LoadOrder:
            await self._start_plugingroup(order)

    async def stop_plugins(self):
        for order in LoadOrder:
            await self._stop_plugingroup(order)

    async def _register_plugingroup(self, order: LoadOrder):
        plugs = self._get_plugins(order)
        for plug in plugs:
            if (plug.testing is True and self.testing_enabled is True) or (
                plug.testing is False
            ):
                plug.register()

    async def _start_plugingroup(self, order: LoadOrder):
        plugs = self._get_plugins(order)
        for plug in plugs:
            if (plug.testing is True and self.testing_enabled is True) or (
                plug.testing is False
            ):
                await plug.start()

    async def _stop_plugingroup(self, order: LoadOrder):
        plugs = self._get_plugins(order)
        for plug in plugs:
            if (plug.testing is True and self.testing_enabled is True) or (
                plug.testing is False
            ):
                await plug.stop()

    def _init_plugins(self):
        for plug in self.plugins:
            if plug.load_order == LoadOrder.Early:
                self.plugins_early.append(plug)
            elif plug.load_order == LoadOrder.Core:
                self.plugins_core.append(plug)
            elif plug.load_order == LoadOrder.Platform:
                self.plugins_platform.append(plug)
            elif plug.load_order == LoadOrder.Storage:
                self.plugins_storage.append(plug)
            elif plug.load_order == LoadOrder.Late:
                self.plugins_late.append(plug)

    def _get_plugins(self, order: LoadOrder) -> list[PluginBase]:
        if order == LoadOrder.Early:
            return self.plugins_early
        elif order == LoadOrder.Core:
            return self.plugins_core
        elif order == LoadOrder.Platform:
            return self.plugins_platform
        elif order == LoadOrder.Storage:
            return self.plugins_storage
        elif order == LoadOrder.Late:
            return self.plugins_late
        else:
            return []
