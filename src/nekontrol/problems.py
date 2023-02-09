import os
import os.path as path
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from typing import Literal

import appdirs
import natsort
import requests

from .config import Config
from .interactive import spinner


@dataclass
class ProblemIO:
    """
    Stores the paths to input, output and a source name.
    """

    i: str
    o: str | None
    from_: Literal["sample"] | Literal["local"]

    def input_name(self):
        return path.basename(self.i)


def problem_dir(problem: str) -> str:
    return path.join(appdirs.user_cache_dir("nekontrol"), "problems", problem)


def download_tests(problem: str, config: Config) -> bool:
    url = f"https://open.kattis.com/problems/{problem}/file/statement/samples.zip"

    problem_cache_dir = problem_dir(problem)

    if path.exists(problem_cache_dir):
        print(f"Using cached sample data for problem {problem}")
        return True
    else:
        with spinner.Spinner(
            f"Downloading sample data for problem {problem} ", color=config.color
        ) as s:
            with requests.get(url, stream=True) as response:
                if not response.ok:
                    s.fail()
                    return False
                with tempfile.TemporaryFile("w+b") as f:
                    shutil.copyfileobj(response.raw, f)
                    f.seek(0)
                    zip = zipfile.ZipFile(f)
                    zip.extractall(problem_cache_dir)
                    s.ok()
                    return True


def problem_sample_inputs_outputs(
    problem: str, config: Config
) -> list[ProblemIO] | None:
    problem_cache_dir = problem_dir(problem)
    downloaded = download_tests(problem, config)

    if not downloaded:
        return None

    in_files = [
        path.join(problem_cache_dir, f)
        for f in os.listdir(problem_cache_dir)
        if f.endswith(".in")
    ]

    def get_out_file(in_file: str) -> str | None:
        out_file = re.sub(r"\.in$", ".ans", in_file)

        return out_file if path.exists(out_file) else None

    ins_and_outs = [(in_file, get_out_file(in_file), "sample") for in_file in in_files]

    return sorted_problems([ProblemIO(*iof) for iof in ins_and_outs])


def local_inputs_outputs(dir: str, name: str) -> list[ProblemIO]:
    file_names = [fn for fn in os.listdir(dir or ".")]

    candidates = [
        (fn, m)
        for fn in file_names
        if (m := re.match("^" + re.escape(name) + r"((?:\.\d+)?)\.in", fn))
    ]

    ins_and_outs: list[ProblemIO] = [
        ProblemIO(
            path.join(dir, in_),
            out
            if path.isfile(out := path.join(dir, name + m.group(1) + ".ans"))
            else None,
            "local",
        )
        for (in_, m) in candidates
    ]

    return sorted_problems(ins_and_outs)


def sorted_problems(
    problems: list[ProblemIO],
) -> list[ProblemIO]:
    return natsort.natsorted(problems, key=lambda p: p.i)
