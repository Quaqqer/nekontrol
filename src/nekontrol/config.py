import os.path as path
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    cpp_libs_dir: str | None = None
    extra_flags: dict[str, list[str]] | None = None
    color: bool = sys.stdout.isatty()
    diff: bool = True
    ignore_debug: bool = True
    verbose: bool = False


def find_config(dir: str) -> str | None:
    p = Path(path.abspath(dir))

    while not path.exists(path.join(p, ".nkconfig.py")):
        if p.parent == p:
            return None

        p = p.parent

    return path.join(p, ".nkconfig.py")


def exec_config(dir: str) -> Config:
    cfg_path = find_config(dir)

    cfg = Config()

    if cfg_path is not None:
        with open(cfg_path, "r") as script:
            exec(script.read(), {"cfg": cfg, "__file__": cfg_path})

    return cfg
