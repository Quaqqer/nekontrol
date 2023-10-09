import os
import tempfile

import termcolor


class TempFileName:
    def __init__(self, *args):
        self.args = args

    def __enter__(self) -> str:
        fd, file_name = tempfile.mkstemp(
            ".exe" if os.name == "nt" else None, *self.args
        )
        os.close(fd)
        self.file_name = file_name
        return self.file_name

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        os.remove(self.file_name)


def indented(s: str) -> str:
    return "\n".join("  " + ds for ds in s.splitlines())


def cw(color: bool):
    """Create a termcolor.colored wrapper that will or will not color the string."""

    def inner(s, *args, **kwargs):
        if color:
            return termcolor.colored(s, *args, **kwargs)
        else:
            return s

    return inner
