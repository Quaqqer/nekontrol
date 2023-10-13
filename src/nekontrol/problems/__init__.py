import asyncio

import natsort

from nekontrol.config import Config
from nekontrol.interactive.tasks import TaskContext

from .sample import ProblemSample
from .source import ProblemSource
from .sources.kattis import KattisSource
from .sources.local import LocalSource


def problem_samples(
    problem: str, source_dir: str, cfg: Config, tctx: TaskContext | None = None
) -> list[ProblemSample]:
    # TODO: No spinners anymore :sad_emoji:, please fix
    sources: list[ProblemSource] = [LocalSource(), KattisSource()]

    samples: list[list[ProblemSample]] = [[] for _ in sources]

    async def fill_samples(i: int):
        src = sources[i]

        task = None

        if tctx is not None:
            task = tctx.add_task(f"{src.source_name}: Fetching")

        samples[i] = src.find_problem(problem, source_dir, cfg=cfg)

        if task is not None:
            if samples[i]:
                task.ok()
            else:
                task.fail()

    asyncio.run(asyncio.wait([fill_samples(i) for i, _ in enumerate(sources)]))

    return [s for src in samples for s in src]


def sorted_problems(
    problems: list[ProblemSample],
) -> list[ProblemSample]:
    return natsort.natsorted(problems, key=lambda p: p.source)
