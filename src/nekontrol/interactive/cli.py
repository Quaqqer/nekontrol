import os.path as path

import click

from nekontrol.console import setup_console
from nekontrol.config import exec_config
from . import commands

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.group()
def cli():
    """nekontrol - Control your kattis solutions."""
    ...


@cli.command("test", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option("-d", "--diff", type=bool)
@click.option("-c", "--color", type=bool)
@click.option("-v", "--verbose", type=bool)
@click.option("--ignore-debug", type=bool)
def test(
    file_path: str,
    problem: str | None,
    color: bool | None,
    diff: bool | None,
    ignore_debug: bool | None,
    verbose: bool | None,
):
    """Run and test against sample and local test data."""
    setup_console(color)

    file_path = path.abspath(file_path)
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

    commands.test.test(file_path, problem, config)


@cli.command("submit", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option(
    "-f", "--force", type=bool, help="Submit even if sample verification fails"
)
@click.option("-c", "--color", type=bool)
@click.option("-v", "--verbose", type=bool)
def submit(
    file_path: str,
    problem: str | None,
    force: bool | None,
    color: bool | None,
    verbose: bool | None,
):
    """Submit a solution to Kattis."""
    setup_console(color)

    file_path = path.abspath(file_path)
    file_dir = path.dirname(file_path)

    config = exec_config(file_dir)

    if color is not None:
        config.color = color
    if force is not None:
        config.force = force
    if verbose is not None:
        config.verbose = verbose

    commands.submit.submit(file_path, problem, config)
