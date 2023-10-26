import click

from nekontrol.config import Config, exec_config
from nekontrol.console import setup_console

from . import commands

executable_file = click.Path(
    exists=True, readable=True, file_okay=True, dir_okay=False, resolve_path=True
)


def config_parser(path_argument: str):
    def inner(f):
        @click.option("--diff/--no-diff", default=None, help="Display diff")
        @click.option("--verbose/--no-verbose", default=None, help="Verbose output")
        @click.option(
            "--ignore-debug/--no-ignore-debug",
            default=None,
            help="Ignore lines starting with `debug`",
        )
        @click.option(
            "--force/--no-force",
            default=None,
            help="Submit even if sample verification fails",
        )
        @click.pass_context
        def wrapper(
            ctx: click.Context,
            *args,
            **kwargs,
        ):
            config = exec_config(kwargs[path_argument])
            for opt in ["diff", "ignore_debug", "verbose", "force"]:
                v = kwargs.pop(opt)
                if v is not None:
                    assert hasattr(config, opt), f"{config} {opt}"
                    config.__setattr__(opt, v)
            return ctx.invoke(f, *args, config=config, **kwargs)

        return wrapper

    return inner


@click.group()
def cli():
    """nekontrol - Control your kattis solutions."""
    ...


@cli.command("test", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@config_parser("file_path")
def test(
    config: Config,
    file_path: str,
    problem: str | None,
):
    """Run and test against sample and local test data."""
    setup_console()

    commands.test.test(file_path, problem, config)


@cli.command("submit", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option("-y", "--yes", is_flag=True)
@config_parser("file_path")
def submit(config: Config, file_path: str, problem: str | None, yes: bool):
    """Submit a solution to Kattis."""
    setup_console()

    commands.submit.submit(file_path, problem, config, yes)
