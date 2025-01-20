"""Proxy registry"""

from typing import Optional
from app.daas.proxy.config import ViewerConfig
from app.daas.proxy.guacamole_proxy import SocketTuple, WebsocketStats


class ProxyRegistry:
    """Proxy registry"""

    def __init__(
        self,
        cfg_proxy: ViewerConfig,
    ):
        self.config = cfg_proxy
        self.active_connections: dict[str, SocketTuple] = {}
        self.closed_connections: dict[str, SocketTuple] = {}
        self.connected = False

    def connect(self):
        """Connects the component"""
        self.connected = True
        return self.connected

    def disconnect(self) -> bool:
        """Disconnects the component"""
        self.connected = False
        return True

    def add_connection(self, info: SocketTuple):
        """Adds new connection"""
        if info.id_instance in self.active_connections:
            old = self.active_connections[info.id_instance]
            info.stats.add(old.stats)
        self.active_connections[info.id_instance] = info

    def get_connection(self, connid: str) -> Optional[SocketTuple]:
        """Returns info object if available"""
        if connid in self.active_connections:
            return self.active_connections[connid]
        return None

    def get_active_connections(self, userid: int = 0) -> dict[str, dict]:
        """Returns all active connections"""
        result = {}
        for connid, info in self.active_connections.items():
            if userid in (0, info.id_owner):
                result[connid] = info.tojson()
        return result

    def get_closed_connections(self, userid: int = 0) -> dict[str, dict]:
        """Returns all closed connections"""
        result = {}
        for connid, info in self.closed_connections.items():
            if userid in (0, info.id_owner):
                result[connid] = info.tojson()
        return result

    def disconnect_connection(self, id_instance: str):
        """Removes connection"""
        info = self.get_connection(id_instance)
        if info is not None:
            self.closed_connections[id_instance] = info
            self.active_connections.pop(id_instance)

    def get_stats_instance(self, id_instance: str) -> Optional[WebsocketStats]:
        """Get stats for specific instance"""
        if id_instance in self.active_connections:
            return self.active_connections[id_instance].stats
        return None

    def get_stats_active(self) -> dict[str, dict]:
        """Returns collection of statistic objects"""
        result = {}
        for connid, info in self.active_connections.items():
            result[connid] = info.stats.tojson()
        return result

    def get_stats_closed(self) -> dict[str, dict]:
        """Returns collection of statistic objects"""
        result = {}
        for connid, info in self.closed_connections.items():
            result[connid] = info.stats.tojson()
        return result

    def get_stats_all(self) -> dict[str, dict]:
        """Returns collection of statistic objects"""
        result = {}
        result.update(self.get_stats_active())
        result.update(self.get_stats_closed())
        return result
