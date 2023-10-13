import shutil
import tempfile
import zipfile

import requests

from nekontrol.config import Config

from ...interactive.tasks import TaskContext
from ..sample import ProblemSample
from ..source import CachedProblemSource
from .local import find_local_sources


class KattisSource(CachedProblemSource):
    source_name = "Kattis"

    def find_uncached(
        self,
        problem: str,
        source_dir: str,
        cfg: Config,
        tctx: TaskContext | None = None,
    ) -> list[ProblemSample]:
        url = f"https://open.kattis.com/problems/{problem}/file/statement/samples.zip"
        with requests.get(url, stream=True) as response:
            if not response.ok:
                # TODO: Maybe we should report that we couldn't fetch anything
                return []

            with tempfile.TemporaryFile("w+b") as f:
                shutil.copyfileobj(response.raw, f)
                f.seek(0)
                zip = zipfile.ZipFile(f)

                with tempfile.TemporaryDirectory() as d:
                    zip.extractall(d)

                    return find_local_sources(lambda _: True, d, "Kattis")
