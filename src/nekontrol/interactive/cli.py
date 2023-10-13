import os.path as path
import re
import time
from lxml.html import fragment_fromstring
from typing import Optional

import click
import requests

from .. import language, problems, util
from ..config import exec_config
from . import run
from .tasks import TaskContext

_HEADERS = {"User-Agent": "nekontrol/0.2.5"}

executable_file = click.Path(exists=True, readable=True, file_okay=True, dir_okay=False)


@click.group()
def cli():
    """nekontrol - Control your kattis solutions."""
    ...


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option("-d", "--diff", type=bool)
@click.option("-c", "--color", type=bool)
@click.option("-v", "--verbose", type=bool)
@click.option("--ignore-debug", type=bool)
def test(
    file_path: str,
    problem: Optional[str],
    color: Optional[bool],
    diff: Optional[bool],
    ignore_debug: Optional[bool],
    verbose: Optional[bool],
):
    """Run and test against sample and local test data."""
    file_path = path.abspath(file_path)
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


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("file-path", metavar="FILE", type=executable_file)
@click.option("-p", "--problem", type=str, help="The kattis problem name")
@click.option(
    "-f", "--force", type=bool, help="Submit even if sample verification fails"
)
@click.option("-c", "--color", type=bool)
@click.option("-v", "--verbose", type=bool)
def submit(
    file_path: str,
    problem: Optional[str],
    force: Optional[bool],
    color: Optional[bool],
    verbose: Optional[bool],
):
    """Submit a solution to Kattis."""
    file_name = path.basename(file_path)
    file_dir = path.dirname(file_path)
    file_base, extension = path.splitext(file_name)

    config = exec_config(file_dir)

    if color is not None:
        config.color = color
    if verbose is not None:
        config.verbose = verbose

    c = util.cw(config.color)

    if problem is None:
        if config.verbose:
            print(c(f"No problem name specified, guessing '{file_base}'", "yellow"))
        problem = file_base

    lang = language.get_lang(file_path, config)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {extension} is not implemented."
        )

    # login
    login = requests.post(
        "https://open.kattis.com/login",
        data={
            "user": "gustav-sornas",
            "token": "1b86a51cda524a88a973d362387a5366f8350306e0ded902c419c112b340f037",
            "script": "true",
        },
        headers=_HEADERS,
    )
    if login.status_code != 200:
        raise click.ClickException(
            f"Failed to login ({login.status_code}):\n{login.text}"
        )

    data = {
        "submit": "true",
        "submit_ctr": 2,
        "language": lang.full_name,
        "mainclass": None,  # TODO: support java, scala, kotlin
        "problem": problem,
        "tag": None,  # TODO: what is this?
        "script": "true",
    }

    with open(file_path) as file:
        files = [
            (
                "sub_file[]",
                (path.basename(file_path), file.read(), "application/octet-stream"),
            )
        ]

    result = requests.post(
        "https://open.kattis.com/submit",
        data=data,
        files=files,
        cookies=login.cookies,
        headers=_HEADERS,
    )

    if result.status_code != 200:
        raise click.ClickException(
            f"Submission failed ({result.status_code}):\n{result.text}"
        )

    _RUNNING_STATUS = 5
    _COMPILE_ERROR_STATUS = 8
    _ACCEPTED_STATUS = 16
    _STATUS_MAP = {
        0: "New",  # <invalid value>
        1: "New",
        2: "Waiting for compile",
        3: "Compiling",
        4: "Waiting for run",
        _RUNNING_STATUS: "Running",
        6: "Judge Error",
        7: "Submission Error",
        _COMPILE_ERROR_STATUS: "Compile Error",
        9: "Run Time Error",
        10: "Memory Limit Exceeded",
        11: "Output Limit Exceeded",
        12: "Time Limit Exceeded",
        13: "Illegal Function",
        14: "Wrong Answer",
        # 15: '<invalid value>',
        _ACCEPTED_STATUS: "Accepted",
    }

    submit_response = result.text
    m = re.search(r"Submission ID: (\d+)", submit_response)
    if m is None:
        print(submit_response)
        raise click.ClickException("Couldn't find submission ID in response.")
    submission_id = m.group(1)
    submission_url = f"https://open.kattis.com/submissions/{submission_id}"

    # poll until done
    while True:
        submission_response = requests.get(
            submission_url + "?json", cookies=login.cookies, headers=_HEADERS
        )
        if submission_response.status_code != 200:
            raise click.ClickException(
                "Error when requesting submission response ({}):\n{}".format(
                    submission_response.status_code, submission_response.text
                )
            )
        status = submission_response.json()
        status_id = status["status_id"]
        testcases_done = status["testcase_index"]
        testcases_total = status["row_html"].count("<i") - 1

        status_text = _STATUS_MAP.get(status_id, f"Unknown status {status_id}")

        if status_id == _COMPILE_ERROR_STATUS:
            print(c(status_text, "red"))
            try:
                root = fragment_fromstring(status["feedback_html"], create_parent=True)
                error = root.find(".//pre").text
                print(c(error, "red"))
            except Exception:
                pass
        elif status_id < _RUNNING_STATUS:
            print(f"{status_text}...")
        elif status_id == _RUNNING_STATUS:
            print("Test cases: ", end="")

            if testcases_total == 0:
                print("???")
            else:
                s = "." * (testcases_done - 1)
                if status_id == _RUNNING_STATUS:
                    s += "?"
                elif status_id == _ACCEPTED_STATUS:
                    s += "."
                else:
                    s += "x"

                print(
                    f"[{s:<{testcases_total}}]  {testcases_done}/{testcases_total}",
                    testcases_total,
                )
        else:
            success = status_id == _ACCEPTED_STATUS
            try:
                root = fragment_fromstring(status["row_html"], create_parent=True)
                cpu_time = root.find('.//*[@data-type="cpu"]').text
                status_text += " (" + cpu_time + ")"
            except Exception:
                pass
            if status_id != _COMPILE_ERROR_STATUS:
                print(c(status_text, "green" if success else "red"))
            return success

        time.sleep(0.25)
