import os
import os.path as path
import sys

import click

from .. import language, problems, util
from . import run
from .spinner import Spinner

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option(
    "-c",
    "--color",
    type=bool,
    default=os.isatty(sys.stdout.fileno()),
    help="If it should output with color or not",
)
def cli(file_path: str, problem: str | None, color: bool):
    """nekontrol - Control your kattis solutions.

    Run FILE and test against sample and local test data.
    """
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

            run.run_all(file_base, [executable], ios, color)
    else:
        cmdline = language.script_cmdline(lang, file_path)
        run.run_all(file_base, cmdline, ios, color)
