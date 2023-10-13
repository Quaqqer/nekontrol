import time

from rich.console import Console
from rich.markup import escape

from nekontrol.interactive.tasks import TaskContext

from .. import compare, util
from ..config import Config
from ..language import Runnable
from ..problems.sample import ProblemSample


def run(
    name: str,
    runnable: Runnable,
    sample: ProblemSample,
    config: Config,
    tctx: TaskContext | None = None,
):
    task_msg = f"Testing with {sample.name}"
    task = tctx.add_task(task_msg) if tctx else None

    start = time.time()
    result = runnable.run(sample.input)
    finish = time.time()
    duration = finish - start

    c = Console()

    bg = "black on bright_red"
    if duration < 1:
        bg = "black on bright_green"
    elif duration < 3:
        bg = "black on bright_yellow"

    time_msg = f"[{bg}] ⏱  {duration:.3} s [/{bg}]"

    task_finished_msg = task_msg + ' ' + time_msg

    diff = None

    if config.diff and sample.output is not None:
        diff = compare.compare_outputs(
            result.stdout, sample.output, sample.input, config
        )

        if isinstance(diff, bool):
            if task:
                task.ok(task_finished_msg)
        else:
            if task:
                task.fail(task_finished_msg)

        if isinstance(diff, str):
            c.print(diff)
        elif diff is True:
            c.print("[on yellow]NOTE: The output contained debug lines")

        if result.exit != 0:
            c.print(
                "[red]Proccess exited with a non-zero exit code {result.exit}"
                + (" and the following stderr:" if result.stderr else "")
            )

            if result.stderr:
                c.print(util.indented(result.stderr), highlight=False)
            return
    else:
        if task:
            task.finish(task_finished_msg)

        c.print("[yellow]Input:")
        c.print(escape(util.indented(sample.input)))
        c.print("[yellow]Got output:")
        c.print(escape(util.indented(result.stdout)))

    if result.stderr:
        c.print("[yellow]Got stderr:")
        print(escape(util.indented(result.stderr)))
