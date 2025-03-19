"""
Helpers for the CommandProxy
"""


def split_command_from_args(args: list):
    """
    Split command from arguments
    taking into account files and folders containing whitespaces
    """
    procname = ""
    rest = []
    if len(args) > 0:
        procname = args[0]
        rest = args[1:]
        if len(args) > 1:
            delims = ("'", '"')
            if procname.startswith(delims):
                for i, element in enumerate(args):
                    if isinstance(element, str) and (
                        element.endswith('"') or element.endswith("'")
                    ):
                        index = i + 1

                        procname = " ".join(args[:index])
                        rest = args[index:]
                        break
    if procname.startswith('"'):
        procname = procname[1:]
    if procname.endswith('"'):
        procname = procname[:-1]
    return procname, rest
