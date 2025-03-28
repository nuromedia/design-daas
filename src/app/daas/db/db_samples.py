"""Bootstrap objects"""

from dataclasses import dataclass
from datetime import datetime
from app.daas.common.model import (
    DaasObject,
    Environment,
    File,
    GuacamoleConnection,
    RessourceInfo,
)
from app.daas.objects.object_application import ApplicationObject
from app.daas.objects.object_machine import MachineObject
from app.daas.objects.object_container import ContainerObject


@dataclass
class SampleRegistryConfig:
    """Config for SampleRegistry"""

    shared_owner: int
    shared_owner_name: str
    test_owner: int
    test_owner_name: str
    default_owner: int
    default_owner_name: str
    default_resolution: str
    persist_files: bool
    persist_apps: bool
    persist_objects: bool
    persist_session: bool


class SampleRegistry:
    """Holds sample information"""

    def __init__(self, cfg: SampleRegistryConfig):
        self.config = cfg

    def create_demo_limits(self):
        owner = self.config.default_owner
        return [
            RessourceInfo(
                id_owner=owner,
                vm_max=-1,
                container_max=-1,
                obj_max=-1,
                cpu_max=12,
                mem_max=12 * 1024**3,
                dsk_max=256 * 1024**3,
            )
        ]

    def create_demo_instances(
        self, obj: DaasObject, env: Environment, con: GuacamoleConnection
    ):
        owner = self.config.default_owner
        return [
            # InstanceObject(
            #     id="randomkey",
            #     id_owner=owner,
            #     app=obj,
            #     host="192.168.223.116",
            #     container="daas.xxx",
            #     created_at=datetime.now(),
            #     connected_at=datetime.now(),
            #     booted_at=datetime.now(),
            #     id_con=con.id,
            #     id_app=obj.id,
            #     id_env=env.id,
            #     env=env,
            # )
        ]

    def create_demo_connection(self):
        return [
            # GuacamoleConnection(
            #     id="randomkey",
            #     user="root",
            #     password="root",
            #     protocol="vnc",
            #     hostname="192.168.223.116",
            #     port=6016,
            #     viewer_url="https://foo.bar.baz",
            #     viewer_token="randomkey2",
            # )
        ]

    def create_demo_environments(self):
        """Create environmenst for testing"""
        owner = self.config.default_owner
        envtasks = [{"args": "", "cmd": "/usr/bin/galculator", "type": "exec_cmd"}]
        envapps = [{"args": "", "cmd": "/usr/bin/galculator", "name": "calc"}]
        envtarget = {"args": "", "cmd": "/usr/bin/galculator", "name": "testname"}
        return [
            # Environment(
            #     id="testenv",
            #     id_object="vmDeb12",
            #     name="envtest",
            #     id_backend="foo",
            #     env_tasks=envtasks,
            #     env_apps=envapps,
            #     env_target=envtarget,
            #     state="environment-final",
            #     created_at=datetime.now(),
            # )
        ]

    def create_demo_objects(self) -> list:
        """Create demo objects"""
        allobj = []
        allobj.extend(self.create_demo_machines())
        allobj.extend(self.create_demo_containers())
        return allobj

    def create_demo_files(self):
        """Create files for testing"""
        owner = self.config.default_owner
        return [
            File(
                id="win10DummyFile",
                id_owner=0,
                os_type="win10",
                name="",
                version="1.2.3",
                localpath=f"/home/design-daas/src/data/shared/{owner}/win10DummyFile.file",
                remotepath="C:/Users/root",
                filesize=79,
                created_at=datetime.now(),
            ),
            File(
                id="win11DummyFile",
                id_owner=0,
                os_type="win11",
                name="",
                version="1.2.3",
                localpath=f"/home/design-daas/src/data/shared/{owner}/win11DummyFile.file",
                remotepath="C:/Users/root",
                filesize=79,
                created_at=datetime.now(),
            ),
            File(
                id="deb12DummyFile",
                id_owner=0,
                os_type="l26",
                name="testfile",
                version="1.2.3",
                localpath=f"/home/design-daas/src/data/shared/{owner}/deb12DummyFile.file",
                remotepath="/root",
                filesize=79,
                created_at=datetime.now(),
            ),
            File(
                id="thunderbirdFile",
                id_owner=0,
                os_type="l26",
                name="thunderbird.exe",
                version="1.2.3",
                localpath=f"/home/design-daas/src/data/shared/{owner}/thunderbirdFile.file",
                remotepath="/root/shared/.wine64/drive_c",
                filesize=79,
                created_at=datetime.now(),
            ),
        ]

    def create_demo_applications(self):
        """Create applications for testing"""
        owner = self.config.shared_owner
        return [
            ApplicationObject(
                id="win10CalcApp",
                id_owner=owner,
                name="win10Calc",
                version="1.2.3",
                id_file=None,
                id_template="templateWin10",
                os_type="win10",
                installer="",
                installer_args="",
                installer_type="exec_cmd",
                target="calc.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win11CalcApp",
                id_owner=owner,
                name="win11Calc",
                version="1.2.3",
                id_file=None,
                id_template="templateWin11",
                os_type="win11",
                installer="",
                installer_args="",
                installer_type="exec_cmd",
                target="calc.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="deb12CalcApp",
                id_owner=owner,
                name="deb12Calc",
                version="1.2.3",
                id_file=None,
                id_template="templateDeb12",
                os_type="l26vm",
                installer="gnome-calculator",
                installer_args="",
                installer_type="os_install",
                target="/usr/bin/gnome-calculator",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="dockerCalcApp",
                id_owner=owner,
                name="x11Calc",
                version="1.2.3",
                id_file=None,
                id_template="contx11",
                os_type="l26",
                installer="gnome-calculator",
                installer_args="",
                installer_type="os_install",
                target="/usr/bin/gnome-calculator",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win10SpreadsheetApp",
                id_owner=owner,
                name="win10Spreadsheet",
                version="1.2.3",
                id_file=None,
                id_template="templateWin10",
                os_type="win10",
                installer="",
                installer_args="",
                installer_type="none",
                target="C:/Program Files/Microsoft Office/root/Office16/Excel.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win11SpreadsheetApp",
                id_owner=owner,
                name="win11Spreadsheet",
                version="1.2.3",
                id_file=None,
                id_template="templateWin11",
                os_type="win11",
                installer="",
                installer_args="",
                installer_type="none",
                target="C:/Program Files/Microsoft Office/root/Office16/Excel.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="deb12SpreadsheetApp",
                id_owner=owner,
                name="deb12Spreadsheet",
                version="1.2.3",
                id_file=None,
                id_template="templateDeb12",
                os_type="l26vm",
                installer="libreoffice",
                installer_args="",
                installer_type="os_install",
                target="libreoffice",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="dockerSpreadsheetApp",
                id_owner=owner,
                name="x11Spreadsheet",
                version="1.2.3",
                id_file=None,
                id_template="contx11",
                os_type="l26",
                installer="libreoffice",
                installer_args="",
                installer_type="os_install",
                target="/usr/bin/libreoffice",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win10TexteditApp",
                id_owner=owner,
                name="win10Textedit",
                version="1.2.3",
                id_file=None,
                id_template="templateWin10",
                os_type="win10",
                installer="Notepad++.Notepad++",
                installer_args="",
                installer_type="os_install",
                target="C:/Program Files/Notepad++/notepad++.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win11TexteditApp",
                id_owner=owner,
                name="win11Textedit",
                version="1.2.3",
                id_file=None,
                id_template="templateWin11",
                os_type="win11",
                installer="Notepad++.Notepad++",
                installer_args="",
                installer_type="os_install",
                target="C:/Program Files/Notepad++/notepad++.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="deb12TexteditApp",
                id_owner=owner,
                name="deb12Textedit",
                version="1.2.3",
                id_file=None,
                id_template="templateDeb12",
                os_type="l26vm",
                installer="gedit",
                installer_args="",
                installer_type="os_install",
                target="gedit",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="dockerTexteditApp",
                id_owner=owner,
                name="x11Textedit",
                version="1.2.3",
                id_file=None,
                id_template="contx11",
                os_type="l26",
                installer="gedit",
                installer_args="-y",
                installer_type="os_install",
                target="gedit",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win10BrowserApp",
                id_owner=owner,
                name="win10Browser",
                version="1.2.3",
                id_file=None,
                id_template="templateWin10",
                os_type="win10",
                installer="",
                installer_args="",
                installer_type="none",
                target="C:/Program Files/Mozilla Firefox/firefox.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="win11BrowserApp",
                id_owner=owner,
                name="win11Browser",
                version="1.2.3",
                id_file=None,
                id_template="templateWin11",
                os_type="win11",
                installer="",
                installer_args="",
                installer_type="none",
                target="C:/Program Files/Mozilla Firefox/firefox.exe",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="deb12BrowserApp",
                id_owner=owner,
                name="deb12Browser",
                version="1.2.3",
                id_file=None,
                id_template="templateDeb12",
                os_type="l26vm",
                installer="firefox-esr",
                installer_args="",
                installer_type="os_install",
                target="firefox-esr",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="dockerBrowserApp",
                id_owner=owner,
                name="x11Browser",
                version="1.2.3",
                id_file=None,
                id_template="contx11",
                os_type="l26",
                installer="firefox-esr",
                installer_args="",
                installer_type="os_install",
                target="firefox-esr",
                target_args="",
                created_at=datetime.now(),
            ),
            ApplicationObject(
                id="wineEmail",
                id_owner=owner,
                name="wineEmail",
                version="1.2.3",
                id_file="thunderbirdFile",
                id_template="contwine",
                os_type="l26",
                installer="wine",
                installer_args="",
                installer_type="none",
                target="wine",
                target_args="/root/shared/.wine64/drive_c/thunderbird.exe",
                created_at=datetime.now(),
            ),
        ]

    def create_demo_machines(self):
        """Create machines for testing"""

        owner = self.config.default_owner
        return [
            MachineObject(
                id="vmWin10",
                id_user="win10vm",
                id_owner=owner,
                id_proxmox=110,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="win10",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=64 * 1024**3,
                vnc_port_system=6010,
                vnc_port_instance=5900,
                viewer_contype="rdp",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            MachineObject(
                id="vmWin11",
                id_user="win11vm",
                id_owner=owner,
                id_proxmox=111,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="win11",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=64 * 1024**3,
                vnc_port_system=6011,
                vnc_port_instance=5900,
                viewer_contype="sysvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            MachineObject(
                id="vmDeb12",
                id_user="deb12vm",
                id_owner=owner,
                id_proxmox=112,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="l26vm",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=32 * 1024**3,
                vnc_port_system=6012,
                vnc_port_instance=5900,
                viewer_contype="sysvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            MachineObject(
                id="templateWin10",
                id_user="win10template",
                id_owner=owner,
                id_proxmox=113,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="win10",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=64 * 1024**3,
                vnc_port_system=6013,
                vnc_port_instance=5900,
                viewer_contype="sysvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            MachineObject(
                id="templateWin11",
                id_user="win11template",
                id_owner=owner,
                id_proxmox=114,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="win11",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=64 * 1024**3,
                vnc_port_system=6014,
                vnc_port_instance=5900,
                viewer_contype="sysvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            MachineObject(
                id="templateDeb12",
                id_user="deb12template",
                id_owner=owner,
                id_proxmox=115,
                id_docker="",
                object_storage="daas-img",
                object_type="vm",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="l26vm",
                hw_cpus=4,
                hw_memory=4 * 1024**3,
                hw_disksize=32 * 1024**3,
                vnc_port_system=6015,
                vnc_port_instance=5900,
                viewer_contype="sysvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="both",
                viewer_resize="browser",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
        ]

    # pylint disable=import-outside-toplevel
    def create_demo_containers(self):
        """Create containers for testing"""

        owner = self.config.default_owner
        return [
            ContainerObject(
                id="contx11",
                id_user="x11container",
                id_owner=owner,
                id_proxmox=-1,
                id_docker="daas.contx11",
                object_storage="local",
                object_type="container",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=False,
                os_type="l26",
                hw_cpus=2,
                hw_memory=4 * 1024**3,
                hw_disksize=8 * 1024**3,
                os_installer=f"/home/design-daas/src/data/docker/{owner}/contx11/Dockerfile",
                vnc_port_system=-1,
                vnc_port_instance=5900,
                viewer_contype="instvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="none",
                viewer_resize="none",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
            ContainerObject(
                id="contwine",
                id_user="winecontainer",
                id_owner=owner,
                id_proxmox=-1,
                id_docker="daas.contwine",
                object_storage="local",
                object_type="container",
                object_mode="stopped",
                object_mode_extended="none",
                object_state="baseimage-create",
                object_tasks=[],
                object_apps=[],
                object_target={},
                ceph_public=False,
                ceph_shared=False,
                ceph_user=False,
                os_wine=True,
                os_type="l26",
                hw_cpus=2,
                hw_memory=4 * 1024**3,
                hw_disksize=8 * 1024**3,
                os_installer=f"/home/design-daas/src/data/docker/{owner}/contwine/Dockerfile",
                vnc_port_system=-1,
                vnc_port_instance=5900,
                viewer_contype="instvnc",
                viewer_resolution=self.config.default_resolution,
                viewer_scale="none",
                viewer_resize="none",
                viewer_dpi=96,
                viewer_force_lossless=False,
            ),
        ]
