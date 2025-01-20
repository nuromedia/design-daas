from dataclasses import dataclass


@dataclass(kw_only=True)
class CephStoreFilesystemFolder:
    """Ceph based filestore"""

    name: str
    src: str
    dst_linux: str
    dst_win: str


@dataclass(kw_only=True)
class CephstoreFilesystemConfig:
    """Config data for Ceph filesystem"""

    enabled: bool
    name: str
    user: str
    folder_public: str
    folder_shared: str
    folder_user: str
    folder_keyrings: str
    folder_mount: str
    mappings_public: CephStoreFilesystemFolder
    mappings_shared: CephStoreFilesystemFolder
    mappings_user: CephStoreFilesystemFolder


@dataclass(kw_only=True)
class CephstoreConfig:
    """Config data for Ceph files"""

    enabled: bool
    daasfs: CephstoreFilesystemConfig
