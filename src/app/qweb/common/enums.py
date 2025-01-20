from enum import Enum


class ScheduledTaskFilter(Enum):
    ALL = "all"
    RUNNING = "running"
    FINAL = "final"
