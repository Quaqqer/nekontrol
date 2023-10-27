import time

from rich.console import Console
from rich.markup import escape

from nekontrol import compare, util
from nekontrol.config import Config
from nekontrol.interactive.tasks import TaskContext
from nekontrol.language import Runnable
from nekontrol.problems.sample import ProblemSample


def run(
    name: str,
    runnable: Runnable,
    sample: ProblemSample,
    config: Config,
    tctx: TaskContext | None = None,
    c: Console = Console(),
) -> bool:
    task_msg = f"Testing with {sample.name}"
    task = tctx.add_task(task_msg) if tctx else None

    start = time.time()
    result = runnable.run(sample.input)
    finish = time.time()
    duration = finish - start

    bg = "black on bright_red"
    if duration < 1:
        bg = "black on bright_green"
    elif duration < 3:
        bg = "black on bright_yellow"

    time_msg = f"[{bg}] ⏱  {duration:.3} s [/{bg}]"

    task_finished_msg = task_msg + " " + time_msg

    if config.diff and sample.output is not None:
        diff = compare.diff(sample.output, result.stdout)

        if diff:
            if task:
                task.fail(task_finished_msg)

            c.print("Input:")
            c.print(escape(util.indented(sample.input)))
            c.print("[yellow]Output:")
            c.print(diff)

            return False
        else:
            if task:
                task.ok(task_finished_msg)

        if result.exit != 0:
            c.print(
                f"[red]Proccess exited with a non-zero exit code {result.exit}"
                + (" and the following stderr:" if result.stderr else "")
            )

            if result.stderr:
                c.print(escape(util.indented(result.stderr)))

            return False
    else:
        if task:
            task.finish(task_finished_msg)

        c.print("[yellow]Input:")
        c.print(escape(util.indented(sample.input)))
        c.print("[yellow]Got output:")
        c.print(escape(util.indented(result.stdout)))

    if result.stderr:
        c.print("[yellow]Got stderr:")
        c.print(escape(util.indented(result.stderr)))

    return True
