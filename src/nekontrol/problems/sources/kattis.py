import shutil
import tempfile
import zipfile

import requests

from ..sample import ProblemSample
from ..source import CachedProblemSource
from .local import LocalSource


class KattisSource(CachedProblemSource):
    source_name = "Kattis"

    def status(self) -> str:
        return "Fetching kattis problem samples"

    def find_problem(self, problem: str, source_path: str) -> list[ProblemSample]:
        url = f"https://open.kattis.com/problems/{problem}/file/statement/samples.zip"
        with requests.get(url, stream=True) as response:
            if not response.ok:
                return []

            with tempfile.TemporaryFile("w+b") as f:
                shutil.copyfileobj(response.raw, f)
                f.seek(0)
                zip = zipfile.ZipFile(f)

                with tempfile.TemporaryDirectory() as d:
                    zip.extractall(d)

                    local = LocalSource()
                    samples = local.find_problem(problem, d)
                    return [
                        ProblemSample(
                            name=s.name,
                            input=s.input,
                            output=s.output,
                            source=self.source_name,
                        )
                        for s in samples
                    ]
