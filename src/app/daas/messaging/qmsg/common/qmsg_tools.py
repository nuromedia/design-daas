"""Tools for message queue"""

import os
import socket


class QMessageTools:
    """Tools for message tools"""

    def get_own_name(self) -> str:
        """Get Hostname"""
        return socket.getfqdn()

    # pylint: disable=import-outside-toplevel
    def get_own_ip(self) -> str:
        """Get ip of first network adapter"""
        if os.name != "posix":
            return socket.gethostbyname(self.get_own_name())
        import netifaces as ni

        interfaces = ni.interfaces()
        for interface in interfaces:
            # Check if the interface has an IPv4 address
            ipv4_info = ni.ifaddresses(interface).get(ni.AF_INET)
            if ipv4_info:
                ip_address = ipv4_info[0]["addr"]
                # Ignore loopback and local addresses                                                                                                                                                                                   -
                if ip_address != "127.0.0.1":
                    return ip_address
        return ""
