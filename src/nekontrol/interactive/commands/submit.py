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
from lxml.html import fragment_fromstring

import click
import requests

from nekontrol import language, util
from . import test

_HEADERS = {"User-Agent": "nekontrol/0.2.5"}


def login(user: str, token: str):
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


def get_submission_id(response):
    m = re.search(r"Submission ID: (\d+)", response)
    if m is None:
        print(response)
        raise click.ClickException("Couldn't find submission ID in response.")
    return m.group(1)


def submit(file_path, problem, config):
    file_name = path.basename(file_path)
    file_base, extension = path.splitext(file_name)

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

    # test before submitting
    test.test(file_path, problem, config)

    if not config.force:
        ans = input("Submit? [Y/n] ")
        if ans.lower() == "n":
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
    poll_submission(c, submission_id, login_cookies)


def poll_submission(c, submission_id, login_cookies):
    """Poll a submission's status until it isn't running."""

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

    submission_url = f"https://open.kattis.com/submissions/{submission_id}"

    while True:
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
