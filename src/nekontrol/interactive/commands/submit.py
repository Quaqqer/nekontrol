# NOTICE
#
# This file's contents is heavily inspired by
# https://github.com/Kattis/kattis-cli, which is licensed under the MIT
# license. Their copyright notice is included here.
#
# KATTIS LICENSE BEGINS
#
#   The MIT License (MIT)
#
#   Copyright (c) 2006-2015 Kattis
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#
# KATTIS LICENSE ENDS

import os.path as path
import re
import time
from dataclasses import dataclass
from typing import TypeAlias, assert_never

import click
import requests
import rich.prompt
from lxml.html import fragment_fromstring
from requests.sessions import RequestsCookieJar
from rich.markup import escape

from nekontrol import language
from nekontrol.config import Config
from nekontrol.console import get_console
from nekontrol.interactive.tasks import Task, TaskContext

from . import test

_HEADERS = {"User-Agent": "nekontrol/0.2.5"}


def login(user: str, token: str) -> RequestsCookieJar:
    r = requests.post(
        "https://open.kattis.com/login",
        data={
            "user": user,
            "token": token,
            "script": "true",
        },
        headers=_HEADERS,
    )
    if r.status_code != 200:
        raise click.ClickException(f"Failed to login ({r.status_code}): {r.text}")
    return r.cookies


def get_submission_id(response_text: str) -> str:
    m = re.search(r"Submission ID: (\d+)", response_text)
    if m is None:
        raise click.ClickException(
            f"Couldn't find submission ID in response: {response_text}."
        )
    return m.group(1)


def submit(file_path: str, problem: str | None, config: Config, yes: bool):
    file_name = path.basename(file_path)
    file_base, extension = path.splitext(file_name)

    c = get_console()

    if problem is None:
        if config.verbose:
            c.print(
                f"[yellow]No problem name specified, guessing '{escape(file_base)}'"
            )
        problem = file_base

    lang = language.get_lang(file_path, config)

    if lang is None:
        raise click.ClickException(
            f"Language for file extension {escape(extension)} is not implemented."
        )

    # test before submitting
    if not config.force:
        test.test(file_path, problem, config)

    if not (
        yes
        or rich.prompt.Confirm.ask("Are you sure you want to submit?", default=False)
    ):
        return

    # login to kattis
    if config.kattis_username is None:
        raise click.ClickException(
            # Align with clicks "Error: " prefix.
            "Missing kattis username in configuration. Please go to\n"
            # Error:
            "       https://open.kattis.com/download/kattisrc and\n"
            "       copy the username and token to your .nkconfig.py."
        )
    if config.kattis_token is None:
        raise click.ClickException(
            # Align with clicks "Error: " prefix.
            "Missing kattis token in configuration. Please go to\n"
            # Error:
            "       https://open.kattis.com/download/kattisrc and\n"
            "       copy the token to your .nkconfig.py."
        )
    login_cookies = login(config.kattis_username, config.kattis_token)

    data = {
        "submit": "true",
        "submit_ctr": 2,
        "language": lang.kattis_name,
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

    r = requests.post(
        "https://open.kattis.com/submit",
        data=data,
        files=files,
        cookies=login_cookies,
        headers=_HEADERS,
    )

    if r.status_code != 200:
        raise click.ClickException(f"Submission failed ({r.status_code}):\n{r.text}")

    submission_id = get_submission_id(r.text)
    live_poll_submission(submission_id, login_cookies)


STATUS_NEW = 0
STATUS_WAIT_COMPILE = 2
STATUS_COMPILING = 3
STATUS_WAIT_RUN = 4
STATUS_RUNNING = 5
STATUS_JUDGE_ERROR = 6
STATUS_SUBMISSION_ERROR = 7
STATUS_COMPILE_ERROR = 8
STATUS_RUNTIME_ERROR = 9
STATUS_MEMORY_EXCEEDED = 10
STATUS_OUTPUT_EXCEEDED = 11
STATUS_TIME_EXCEEDED = 12
STATUS_ILLEGAL_FUNCTION = 13
STATUS_WRONG_ANSWER = 14
STATUS_ACCEPTED = 16


def get_status_message(status: int) -> str:
    STATUS_MESSAGES = {
        STATUS_NEW: "New",
        STATUS_WAIT_COMPILE: "Waiting for compile",
        STATUS_COMPILING: "Compiling",
        STATUS_WAIT_RUN: "Waiting for run",
        STATUS_RUNNING: "Running",
        STATUS_JUDGE_ERROR: "Judge Error",
        STATUS_SUBMISSION_ERROR: "Submission Error",
        STATUS_COMPILE_ERROR: "Compile Error",
        STATUS_RUNTIME_ERROR: "Run Time Error",
        STATUS_MEMORY_EXCEEDED: "Memory Limit Exceeded",
        STATUS_OUTPUT_EXCEEDED: "Output Limit Exceeded",
        STATUS_TIME_EXCEEDED: "Time Limit Exceeded",
        STATUS_ILLEGAL_FUNCTION: "Illegal Function",
        STATUS_WRONG_ANSWER: "Wrong Answer",
        STATUS_ACCEPTED: "Accepted",
    }
    return STATUS_MESSAGES.get(status, "Unknown status")


@dataclass
class PollStatusPreparing:
    msg: str


@dataclass
class PollStatusPrepareErr:
    msg: str


@dataclass
class PollStatusRunning:
    total_test_cases: int
    successful_test_cases: int


@dataclass
class PollStatusAccepted:
    total_test_cases: int


@dataclass
class PollStatusErr:
    status: int
    total_test_cases: int
    successful_test_cases: int
    msg: str


PollStatus: TypeAlias = "PollStatusPreparing | PollStatusPrepareErr | PollStatusRunning | PollStatusAccepted | PollStatusErr"  # noqa


def poll(submission_id: str, login_cookies: RequestsCookieJar) -> PollStatus:
    """Poll a submission status"""

    submission_url = f"https://open.kattis.com/submissions/{submission_id}"
    submission_response = requests.get(
        submission_url + "?json", cookies=login_cookies, headers=_HEADERS
    )

    if submission_response.status_code != 200:
        raise click.ClickException(
            "Error when requesting submission response ({}):\n{}".format(
                submission_response.status_code, submission_response.text
            )
        )

    status = submission_response.json()
    status_id = status["status_id"]
    testcases_done = status["testcase_index"] - 1
    testcases_total = status["row_html"].count("<i") - 1

    if status_id == STATUS_COMPILE_ERROR:
        msg = f"[red]{get_status_message(status_id)}[/red]"

        try:
            root = fragment_fromstring(status["feedback_html"], create_parent=True)
            error = root.find(".//pre").text
            msg += f"\n[red]{escape(error)}[/red]"
        except Exception:
            pass

        return PollStatusPrepareErr(msg=msg)
    elif status_id < STATUS_RUNNING:
        return PollStatusPreparing(f"{get_status_message(status_id)}")
    elif status_id == STATUS_RUNNING:
        return PollStatusRunning(
            total_test_cases=testcases_total, successful_test_cases=testcases_done
        )
    elif status_id == STATUS_ACCEPTED:
        return PollStatusAccepted(total_test_cases=testcases_total)
    else:  # some kind of error occurred
        msg = get_status_message(status_id)

        try:  # to get cpu time if possible
            root = fragment_fromstring(status["row_html"], create_parent=True)
            cpu_time = root.find('.//*[@data-type="cpu"]').text
            msg += " (" + cpu_time + ")"
        except Exception:
            pass

        return PollStatusErr(
            status=status_id,
            total_test_cases=testcases_total,
            successful_test_cases=testcases_done,
            msg=msg,
        )


def live_poll_submission(submission_id, login_cookies):
    """Poll a submission's status until it isn't running."""

    with TaskContext() as tctx:
        prepare_task: Task = tctx.add_task("Preparing: New...")
        running_task: Task | None = None

        while True:
            status = poll(submission_id, login_cookies)

            check = r"[green]\[✓] [/green]"
            cross = r"[red]\[✕] [/red]"
            quest = r"[blue]\[?] [/blue]"

            match status:
                case PollStatusPreparing(msg=msg):
                    prepare_task.msg = f"Preparing: {escape(msg)}..."
                case PollStatusPrepareErr(msg=msg):
                    prepare_task.fail(f"Preparing: {msg}")
                    break
                case PollStatusRunning(
                    total_test_cases=total_test_cases,
                    successful_test_cases=successful_test_cases,
                ):
                    prepare_task.ok("Preparing: Ok")

                    rest = total_test_cases - successful_test_cases
                    checks = check * successful_test_cases + quest * rest
                    msg = f"Running: {checks}"

                    if not running_task:
                        running_task = tctx.add_task(msg)
                    else:
                        running_task.msg = msg
                case PollStatusAccepted(total_test_cases=total_test_cases):
                    prepare_task.ok("Preparing: Ok")

                    msg = f"Running: {check * total_test_cases}"
                    if running_task:
                        running_task.ok(msg)
                    else:
                        running_task = tctx.add_task(msg)
                        running_task.ok()
                    break
                case PollStatusErr(
                    total_test_cases=total_test_cases,
                    successful_test_cases=successful_test_cases,
                    msg=status_err,
                ):
                    prepare_task.ok("Preparing: Ok")

                    rest = total_test_cases - successful_test_cases - 1
                    checks = check * successful_test_cases + cross + quest * rest
                    msg = f"Running: {checks}"

                    if running_task:
                        running_task.fail(msg)
                    else:
                        running_task = tctx.add_task(msg)
                        running_task.fail()
                    c = tctx.console
                    c.print(
                        f"Error on test case {successful_test_cases + 1}:"
                        f" {escape(status_err)}"
                    )
                    break
                case _:
                    assert_never(status)

            time.sleep(0.25)
