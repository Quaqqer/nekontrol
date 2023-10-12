import natsort

from nekontrol.config import Config

from .sample import ProblemSample
from .source import ProblemSource
from .sources.kattis import KattisSource
from .sources.local import LocalSource


def problem_samples(problem: str, source_dir: str, cfg: Config) -> list[ProblemSample]:
    sources: list[ProblemSource] = [LocalSource(), KattisSource()]

    # TODO: No spinners anymore :(, please fix

    samples = [
        sample
        for source in sources
        for sample in sorted_problems(source.find_problem(problem, source_dir, cfg))
    ]

    return samples


def sorted_problems(
    problems: list[ProblemSample],
) -> list[ProblemSample]:
    return natsort.natsorted(problems, key=lambda p: p.source)
