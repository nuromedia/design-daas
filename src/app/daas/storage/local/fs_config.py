from dataclasses import dataclass


@dataclass(kw_only=True)
class FilestoreConfig:
    """Config data for Filestore"""

    folder_upload: str
    """Folder for user uploads"""

    folder_shared: str
    """Folder for shared user uploads"""

    folder_tmp: str
    """Global temp folder"""

    folder_docker: str
    """Global dockerfile folder"""

    folder_endpoint_info: str
    """Global dockerfile folder"""

    folder_inst_status: str
    """Instance status folder"""

    folder_inst_env: str
    """Instance env folder"""

    instance_status_outfile_name: str
    """The filename where output is stored"""

    instance_status_pidfile_name: str
    """The filename where the current pid is stored"""

    default_wine_image_folder: str
    """Folder of root image wine"""

    default_wine_image_name: str
    """Name of root image wine"""

    default_x11vnc_image_folder: str
    """Folder of root image x11vnc"""

    default_x11vnc_image_name: str
    """Name of root image x11vnc"""
