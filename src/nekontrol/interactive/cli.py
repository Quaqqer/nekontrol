import functools
import os.path as path

import click

from .. import kattis, language, problems, util
from ..config import Config, exec_config
from . import run

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


def config(f):
    """Wrapper to get parse config and bundle it.

    Expects the user to wrap this wrapper such that it gets a file_path argument.
    Expects the wrapped function to take an argument 'config'.

    Args:
        f (Callable): The function to wrap

    Returns:
        The wrapped function
    """

    @click.option("-d", "--diff", type=bool, help="If it should display a diff")
    @click.option("-c", "--color", type=bool, help="If there should be color")
    @click.option("-v", "--verbose", type=bool, help="If the output should be verbose")
    @click.option("--ignore-debug", type=bool, help="If it should ignore debug lines")
    @functools.wraps(f)
    def wrapper(
        *args,
        file_path: str,
        diff: bool | None,
        color: bool | None,
        verbose: bool | None,
        ignore_debug: bool | None,
        **kwargs,
    ):
        file_dir = path.dirname(file_path)

        config = exec_config(file_dir)
        if color is not None:
            config.color = color
        if diff is not None:
            config.diff = diff
        if ignore_debug is not None:
            config.ignore_debug = ignore_debug
        if verbose is not None:
            config.verbose = verbose

        return f(*args, **kwargs | {"config": config, "file_path": file_path})

    return wrapper


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """nekontrol - Control your kattis solutions"""


def _test(
    lang: language.Language,
    problem: str,
    config: Config,
    file_dir: str,
    file_base: str,
    file_name: str,
) -> bool:
    ios = problems.inputs_outputs(problem, config, file_dir, file_base)

    if len(ios) == 0:
        raise click.ClickException(f"Found no inputs to run for problem {problem}")

    with lang:
        return all([run.run(file_name, lang, io, config) for io in ios])


@cli.command()
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@config
def test(file_path: str, problem: str | None, config: Config):
    """Run FILE and test against sample and local test data"""
    file_name = path.basename(file_path)
    file_base, extension = path.splitext(file_name)

    c = util.cw(config.color)

    if problem is None:
        if config.verbose:
            print(c(f"No problem name specified, guessing '{file_base}'", "yellow"))
        problem = file_base

    lang = language.get_lang(file_path, config)
    file_dir = path.dirname(file_path)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )

    _test(lang, problem, config, file_dir, file_base, file_name)


@cli.command()
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option(
    "-f",
    "--force/--no-force",
    default=False,
    help="Force submission even if it fails the tests",
)
@config
def submit(file_path: str, problem: str | None, config: Config, force: bool):
    file_name = path.basename(file_path)
    file_base, extension = path.splitext(file_name)

    c = util.cw(config.color)

    if problem is None:
        if config.verbose:
            print(c(f"No problem name specified, guessing '{file_base}'", "yellow"))
        problem = file_base

    lang = language.get_lang(file_path, config)
    file_dir = path.dirname(file_path)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )
    ok = force or _test(lang, problem, config, file_dir, file_base, file_name)

    c = util.cw(config.color)

    if ok:
        kattis.submit(lang, problem)
