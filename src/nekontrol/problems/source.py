from abc import ABC

from .sample import ProblemSample


class ProblemSource(ABC):
    source_name: str

    def status(self) -> str:
        raise NotImplementedError()

    def find_problem(self, problem_name: str, source_path: str) -> list[ProblemSample]:
        raise NotImplementedError()


class CachedProblemSource(ProblemSource):
    pass
