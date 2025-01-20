"""Baseclass for endpoint permissions"""

import os
import json
from pathlib import Path
from app.daas.storage.local.fs_config import FilestoreConfig
from app.daas.storage.local.fs_base import FilestoreBase


class FilestorePermissions(FilestoreBase):
    """Baseclass for endpoint permissions"""

    def __init__(self, config: FilestoreConfig):
        super().__init__(config)
        self.config = config
        self.permission_groups: dict[str, dict] = {}
        self.permissions_by_id: dict[int, str] = {}
        self.permissions_by_name: dict[str, int] = {}

    async def initialize_permissions(self) -> bool:
        folder = await self.get_base_folder_endpoint_info()
        success = await self.read_endpoint_info(folder)
        size_map_groups = len(self.permission_groups)
        size_map_id = len(self.permissions_by_id)
        size_map_name = len(self.permissions_by_name)
        self._log_info(f"Endpoint Groups   : {size_map_groups}")
        self._log_info(f"Endpoint Mappings : {size_map_id} {size_map_name}")
        self._log_info(f"Endpoint Success  : {success}")
        return success

    async def get_permission_group(self, name: str) -> dict:
        """
        Retrieves the permission group specified by name
        """
        if name in self.permission_groups:
            return self.permission_groups[name]
        return {}

    async def get_permission_by_id(self, id: int) -> str:
        """
        Retrieves the permission specified by id
        """
        if id in self.permissions_by_id:
            return self.permissions_by_id[id]
        return ""

    async def get_permission_by_name(self, name: str) -> int:
        """
        Retrieves the permission specified by name
        """
        if name in self.permissions_by_name:
            return self.permissions_by_name[name]
        return -1

    async def read_endpoint_info(self, folder: str) -> bool:
        """Reads endpoint info"""
        for file in os.listdir(folder):
            filename = f"{folder}/{os.fsdecode(file)}"
            if filename.endswith(".json"):
                group = Path(filename).stem
                obj = await self.__read_endpoint_group(group, filename)
                if "endpoints" in obj:
                    for endpoint in obj["endpoints"]:
                        info_read = await self.__read_endpoint_object(endpoint)
                        if info_read is False:
                            break
        return await self.__check_endpoint_success()

    async def __check_endpoint_success(self) -> bool:
        result = True
        size_map_groups = len(self.permission_groups)
        size_map_id = len(self.permissions_by_id)
        size_map_name = len(self.permissions_by_name)
        if size_map_groups == 0 or size_map_id == 0 or size_map_id != size_map_name:
            result = False
        return result

    async def __read_endpoint_object(self, endpoint: dict):
        result = True
        if "unique_permission_id" in endpoint and "function_name" in endpoint:
            id = endpoint["unique_permission_id"]
            name = endpoint["function_name"]
            self.permissions_by_id[id] = name
            self.permissions_by_name[name] = id
        else:
            result = False
        return result

    async def __read_endpoint_group(self, group_name: str, filename: str) -> dict:
        with open(filename, "r", encoding="utf-8") as file_obj:
            json_group = json.load(file_obj)
            self.permission_groups[group_name] = json_group
            return json_group
