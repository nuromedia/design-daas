"""Test object definitions"""

from enum import Enum
from typing import Any, Optional
from app.daas.common.enums import BackendName
from app.qweb.service.service_context import LayerObject, QwebBackend, QwebObjectLayer


class TestpluginObject(Enum):
    """Testplugin object type"""

    UNKNOWN = 1
    TESTOBJECT = 2


class TestBackend(QwebBackend):
    """Test backend"""

    def __init__(self):
        QwebBackend.__init__(
            self, BackendName.TESTING.value, [{"id": "abc"}, {"id": "def"}]
        )

    def status(self) -> str:
        """Returns status message"""
        state = "Inactive"
        if self.connected and self.registered:
            state = "Active"
        return f"{state}"

    async def connect(self) -> bool:
        """Connects database adapter"""
        self.connected = True
        return True

    async def disconnect(self) -> bool:
        """Disconnects database adapter"""
        self.connected = False
        return True


class TestObjectLayer(QwebObjectLayer):
    """Testlayer for objects"""

    async def get_object(self, obj: LayerObject, args: dict) -> Optional[Any]:
        """Returns plugin objects"""
        result = None
        if obj.objtype == str(TestpluginObject.TESTOBJECT):
            if isinstance(self.backend.component, list):
                testid = args["id"]
                for item in self.backend.component:
                    if "id" in item and item["id"] == testid:
                        result = item
        return result
