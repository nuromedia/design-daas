from dataclasses import dataclass
from app.qweb.common.common import SystemTaskArgs


@dataclass
class CloneTaskConfig:
    args: SystemTaskArgs


@dataclass
class CreateTaskConfig:
    args: SystemTaskArgs


@dataclass
class TasklistObject:
    type: str
    cmd: str
    args: str


@dataclass
class ApplistObject:
    name: str
    cmd: str
    args: str


@dataclass
class TargetObject:
    name: str
    cmd: str
    args: str
