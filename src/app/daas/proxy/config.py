from dataclasses import dataclass


@dataclass(kw_only=True)
class ViewerConfig:
    """Config data for viewer"""

    guacd: str
    """
    Connection to the Guacd proxy.
    Example value: `"GUACD=192.0.2.1:4822"`
    """

    viewer_protocol: str
    """
    The viewer protocol (http or https)
    """

    viewer_host: str
    """
    The viewer hostname or ip
    """

    viewer_port: int
    """
    The viewer port
    """

    token_length: int
    """
    Length of security token for the connection
    """

    observer_ms: int = 250
    """
    ResizeObserver timings
    """

    fetch_ms: int = 3000
    """
    fetch settings interval
    """

    check_ms: int = 1000
    """
    interval used for boot check
    """

    reconnect_min_ms: int = 250
    """
    Default reconnect delay
    """

    reconnect_default_ms: int = 1000
    """
    Viewer reconnect delay on error in ms
    """
    reconnect_delayed_ms: int = 10000
    """
    Viewer extended reconnect delay on error in ms
    """
    reconnect_max: int = 10
    """
    Maximum recionnects before extended delays
    """

    reconnect_enabled: int = 1
    """
    Use reconnect instead of reload where possible
    """
