"""Timings helpers and definitions"""

import time
from dataclasses import asdict, dataclass, field


@dataclass
class Timespan:
    """Specifies a timespan"""

    begin: int = 0
    end: int = 0
    diff: int = 0

    def start(self):
        """Sets first timestamp"""
        self.begin = self.get_timestamp()

    def stop(self):
        """Sets second timestamp"""
        self.end = self.get_timestamp()
        self.diff = self.end - self.begin

    def get_timestamp(self):
        """Create timestamp"""
        return round(time.time_ns() / 1000000)

    def to_json(self):
        """Converts object to json"""
        return asdict(self)


@dataclass
class Measurement:
    """Measurements taken during processing"""

    request_delay: int = 0
    request: Timespan = field(default_factory=Timespan)
    authentication: Timespan = field(default_factory=Timespan)
    processing: Timespan = field(default_factory=Timespan)
    context: Timespan = field(default_factory=Timespan)

    def start(self, cli_ms: int = -1):
        """Sets first timestamp"""
        self.request = Timespan()
        self.processing = Timespan()
        self.authentication = Timespan()
        self.context = Timespan()
        self.request.start()
        if cli_ms == -1:
            self.request_delay = 0
        else:
            self.request_delay = self.request.begin - cli_ms

    def stop(self):
        """Sets second timestamp"""
        self.request.stop()

    def to_json(self):
        """Converts object to json"""
        return asdict(self)
