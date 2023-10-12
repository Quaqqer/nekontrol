import natsort

from .sample import ProblemSample
from .source import ProblemSource
from .sources.kattis import KattisSource
from .sources.local import LocalSource


def problem_samples(problem: str, source_path: str) -> list[ProblemSample]:
    sources: list[ProblemSource] = [LocalSource(), KattisSource()]

    samples = [
        sample
        for source in sources
        for sample in sorted_problems(source.find_problem(problem, source_path))
    ]

    return samples


def sorted_problems(
    problems: list[ProblemSample],
) -> list[ProblemSample]:
    return natsort.natsorted(problems, key=lambda p: p.source)
