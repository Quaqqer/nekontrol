import os
import re
from os import path

from nekontrol.problems.sample import ProblemSample

from ..source import ProblemSource


class LocalSource(ProblemSource):
    source_name = "Local samples"

    def status(self) -> str:
        return "Fetching local problem samples"

    def find_problem(self, problem_name: str, source_path: str) -> list[ProblemSample]:
        source_dir = path.dirname(source_path)

        samples: list[ProblemSample] = []

        for file in os.listdir(source_dir):
            if file.endswith(".in"):
                input_path = path.join(source_dir, file)

                with open(file) as f:
                    input = f.read()

                output = None
                output_path = re.sub(r".in$", ".ans", input_path)
                if path.exists(output_path):
                    with open(output_path) as f:
                        output = f.read()

                samples.append(
                    ProblemSample(
                        name=path.basename(file),
                        source=self.source_name,
                        input=input,
                        output=output,
                    )
                )

        return samples
