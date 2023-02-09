import os
import os.path as path
import sys

import click

from .. import config, language, problems, util
from . import run
from .spinner import Spinner

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option("--diff/--no-diff", default=True)
@click.option(
    "-c",
    "--color",
    type=bool,
    default=os.isatty(sys.stdout.fileno()),
    help="If it should output with color or not",
)
def cli(file_path: str, problem: str | None, color: bool, diff: bool):
    """nekontrol - Control your kattis solutions.

    Run FILE and test against sample and local test data.
    """
    file_name = path.basename(file_path)
    file_dir = path.dirname(file_path)
    file_base, extension = path.splitext(file_name)

    cfg = config.exec_config(file_dir)

    c = util.cw(cfg.color)

    if problem is None:
        print(c(f"No problem name specified, guessing '{file_base}'", "yellow"))
        problem = file_base

    local_ios = problems.local_inputs_outputs(file_dir, file_base)
    sample_ios = problems.problem_sample_inputs_outputs(problem)
    ios = local_ios + (sample_ios or [])

    if len(ios) == 0:
        raise click.ClickException(f"Found no inputs to run for problem {problem}")

    lang = language.get_lang(file_path, cfg)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )

    with lang:
        for input_file in [i for i, o, from_ in ios]:
            exit_code, stdout, stderr = lang.run(input_file)

            if exit_code == 0:
                pass
            else:
                pass
