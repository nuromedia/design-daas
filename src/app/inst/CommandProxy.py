#!/usr/bin/python3

import os
import sys
import click
from ProxyControl import ProxyControl
from adapter.tools.ProxyTools import split_command_from_args


DEBUG_MODE = False
# DEBUG_MODE = True


def __initialize_component(mode: bool):
    if mode is False:
        username = "root"
        statusfile = "cmdout.txt"
        statusfolder = f"C:/Users/{username}/daas/status"
        if os.name == "posix":
            statusfolder = "/root/daas/status"

        if os.path.exists(statusfolder) is False:
            os.makedirs(statusfolder)
        sys.stdout = open(f"{statusfolder}/{statusfile}", "w")


@click.group
def clickproxy():
    """
    Spawns a new process with specified parameters
    """


@clickproxy.command
@click.argument("args", nargs=-1)
def app(args: list):
    """
    Invokes app with specified arguments
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    ret = proxy.execute_app(cmd_parsed, args_parsed)
    return ret


@clickproxy.command
@click.argument("args", nargs=-1)
def cmd(args: list):
    """
    Invokes api command with specified arguments
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    return proxy.execute_cmd(cmd_parsed, args_parsed)


@clickproxy.command
@click.argument("args", nargs=-1)
def action(args: list):
    """
    Invokes api action with specified arguments
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    return proxy.execute_action(cmd_parsed, args_parsed)


@clickproxy.command
@click.argument("args", nargs=-1)
def resolution(args: list):
    """
    Invokes api commands to control screen reolutions
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    return proxy.execute_resolution(cmd_parsed, args_parsed)


@clickproxy.command
@click.argument("args", nargs=-1)
def ospackage(args: list):
    """
    Invokes api commands to control native ospackages
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    return proxy.execute_ospackage(cmd_parsed, args_parsed)


@clickproxy.command
@click.argument("args", nargs=-1)
def filesystem(args: list):
    """
    Invokes api commands to manage filesystem
    """
    proxy = ProxyControl()
    cmd_parsed, args_parsed = split_command_from_args(args)
    return proxy.execute_filesystem(cmd_parsed, args_parsed)


if __name__ == "__main__":
    __initialize_component(DEBUG_MODE)
    clickproxy()
