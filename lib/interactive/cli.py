import os
import os.path as path
import sys

import click

from .. import language, problems, util
from . import run
from .spinner import Spinner

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.command()
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("--problem", type=str)
@click.option("--color", type=bool, default=os.isatty(sys.stdout.fileno()))
def cli(file_path: str, problem: str | None, color: bool):
    file_name = path.basename(file_path)
    file_dir = path.dirname(file_path)
    file_base, extension = path.splitext(file_name)

    if problem is None:
        print(f"No problem name specified, guessing '{file_base}'")
        problem = file_base

    local_ios = problems.local_inputs_outputs(file_dir, file_base)
    sample_ios = problems.problem_sample_inputs_outputs(problem)
    ios = local_ios + (sample_ios or [])

    if len(ios) == 0:
        print(f"Found no inputs to run for problem {problem}")
        exit()

    lang = language.extension_lang(extension)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )

    if language.is_compiled(lang):
        with util.TempFileName() as executable:
            with Spinner(f"Compiling {file_path} ") as spinner:
                compile_errors = language.compile(file_path, lang, executable, color)
                spinner.ok(compile_errors is None)

            if compile_errors is not None:
                print(compile_errors)
                exit(1)

            run.run_all(file_base, [executable], ios)
    else:
        cmdline = language.script_cmdline(lang, file_path)
        run.run_all(file_base, cmdline, ios)
