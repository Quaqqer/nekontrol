import json
import os
from abc import ABC
from os import path

import appdirs
from typing_extensions import override

from nekontrol.config import Config
from nekontrol.interactive.tasks import TaskContext

from .sample import ProblemSample


class ProblemSource(ABC):
    source_name: str

    def find_problem(
        self,
        problem: str,
        source_dir: str,
        cfg: Config,
        tctx: TaskContext | None = None,
    ) -> list[ProblemSample]:
        raise NotImplementedError()


class CachedProblemSource(ProblemSource):
    def cache_dir(self) -> str:
        cache_dir = appdirs.user_cache_dir("nekontrol")
        source_cache_dir = path.join(cache_dir, "sources", self.source_name)
        return source_cache_dir

    def write_cached_samples(self, problem: str, samples: list[ProblemSample]):
        cd = self.cache_dir()
        json_path = path.join(cd, f"{problem}.json")

        j = [sample.to_json() for sample in samples]

        if not path.exists(cd):
            os.makedirs(cd)
        with open(json_path, "w+") as f:
            f.write(json.dumps(j))

    def read_cached_samples(self, problem: str) -> list[ProblemSample] | None:
        cd = self.cache_dir()

        json_path = path.join(cd, f"{problem}.json")

        if not path.exists(json_path):
            return None

        with open(json_path, "r") as f:
            j = json.loads(f.read())
        samples = [ProblemSample.from_json(o) for o in j]
        return samples

    @override
    def find_problem(
        self,
        problem: str,
        source_dir: str,
        cfg: Config,
        tctx: TaskContext | None = None,
    ) -> list[ProblemSample]:
        cached = self.read_cached_samples(problem)

        if cached is not None:
            return cached

        uncached = self.find_uncached(problem, source_dir, cfg, tctx=tctx)
        self.write_cached_samples(problem, uncached)

        return uncached

    def find_uncached(
        self,
        problem: str,
        source_dir: str,
        cfg: Config,
        tctx: TaskContext | None = None,
    ) -> list[ProblemSample]:
        raise NotImplementedError()
