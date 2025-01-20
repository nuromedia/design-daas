from dataclasses import dataclass


@dataclass(kw_only=True)
class SysteminfoConfig:
    """Config data for Systeminfo tool"""

    known_daas_containers: list
    known_daas_images: list
    known_daas_vms: list
    excluded_object_properties: list
    system_object_owner: int
