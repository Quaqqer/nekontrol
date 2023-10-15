import os.path as path

import click
from rich.console import Console

from nekontrol import language, problems
from ..tasks import TaskContext
from . import run


def test(file_path, problem, config):
    file_path = path.abspath(file_path)
    file_name = path.basename(file_path)
    file_dir = path.dirname(file_path)
    file_base, extension = path.splitext(file_name)

    c = Console()

    if problem is None:
        if config.verbose:
            c.print(f"[yellow]No problem name specified, guessing '{file_base}'")
        problem = file_base

    with TaskContext() as tctx:
        samples = problems.problem_samples(file_base, file_dir, config, tctx=tctx)

        if len(samples) == 0:
            raise click.ClickException(f"Found no inputs to run for problem {problem}")

        lang = language.get_lang(file_path, config, tctx=tctx)

        if lang is None:
            raise click.ClickException(
                f"Language for file extension {extension} is not implemented."
            )

        with lang as runnable:
            for sample in samples:
                run.run(file_name, runnable, sample, config, tctx=tctx)
