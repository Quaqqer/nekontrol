from rich.console import Console

_console = None


def setup_console(color: bool | None):
    global _console
    if _console is None:
        color_system = None if color is False else "auto"
        _console = Console(color_system=color_system)
    return _console


def get_console() -> Console:
    if _console is None:
        raise Exception("setup_console not called")
    return _console
