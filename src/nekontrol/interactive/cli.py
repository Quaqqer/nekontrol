import os.path as path

import click

from .. import language, problems, util
from ..config import exec_config
from . import run

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option("-d", "--diff", type=bool)
@click.option("-c", "--color", type=bool)
@click.option("-v", "--verbose", type=bool)
@click.option("--ignore-debug", type=bool)
def cli(
    file_path: str,
    problem: str | None,
    color: bool | None,
    diff: bool | None,
    ignore_debug: bool | None,
    verbose: bool | None,
):
    """nekontrol - Control your kattis solutions.

    Run FILE and test against sample and local test data.
    """
    file_name = path.basename(file_path)
    file_dir = path.dirname(file_path)
    file_base, extension = path.splitext(file_name)

    config = exec_config(file_dir)
    if color is not None:
        config.color = color
    if diff is not None:
        config.diff = diff
    if ignore_debug is not None:
        config.ignore_debug = ignore_debug
    if verbose is not None:
        config.verbose = verbose

    c = util.cw(config.color)

    if problem is None:
        if config.verbose:
            print(c(f"No problem name specified, guessing '{file_base}'", "yellow"))
        problem = file_base

    local_ios = problems.local_inputs_outputs(file_dir, file_base)
    sample_ios = problems.problem_sample_inputs_outputs(problem, config)
    ios = local_ios + (sample_ios or [])

    if len(ios) == 0:
        raise click.ClickException(f"Found no inputs to run for problem {problem}")

    lang = language.get_lang(file_path, config)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )

    with lang:
        for io in ios:
            run.run(file_name, lang, io, config)
