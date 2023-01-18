import os
import tempfile


class TempFileName:
    def __init__(self, *args):
        self.args = args

    def __enter__(self) -> str:
        fd, file_name = tempfile.mkstemp(*self.args)
        os.close(fd)
        self.file_name = file_name
        return self.file_name

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.file_name)


def indented(s: str) -> str:
    return "\n".join("  " + ds for ds in s.splitlines())
