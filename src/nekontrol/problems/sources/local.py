import os
import re
from os import path
from typing import Callable

from nekontrol.config import Config
from nekontrol.problems.sample import ProblemSample

from ...interactive.tasks import TaskContext
from ..source import ProblemSource


def find_local_sources(filter: Callable[[str], bool], source_dir: str, source: str):
    """
    filter: Filter by (file_name)
    """
    samples: list[ProblemSample] = []

    for file in os.listdir(source_dir):
        if filter(file) and file.endswith(".in"):
            input_path = path.join(source_dir, file)

            with open(input_path) as f:
                input = f.read()

            output = None
            output_path = re.sub(r".in$", ".ans", input_path)
            if path.exists(output_path):
                with open(path.join(source_dir, output_path)) as f:
                    output = f.read()

            samples.append(
                ProblemSample(
                    name=path.basename(file),
                    source=source,
                    input=input,
                    output=output,
                )
            )

    return samples


class LocalSource(ProblemSource):
    source_name = "Local samples"

    def find_problem(
        self,
        problem: str,
        source_dir: str,
        cfg: Config,
        tctx: TaskContext | None = None,
    ) -> list[ProblemSample]:
        return find_local_sources(
            lambda fname: fname.startswith(problem), source_dir, "Local"
        )
