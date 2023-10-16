from rich.console import Console

_console = None


def setup_console():
    global _console
    if _console is None:
        _console = Console()
    return _console


def get_console() -> Console:
    if _console is None:
        raise Exception("setup_console not called")
    return _console
