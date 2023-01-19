import os
import os.path as path
import subprocess
import sys

from .. import compare, util
from . import spinner


def run_all(
    name: str, cmdline: list[str], ios: list[tuple[str, str | None, str]], color: bool
):
    for i, o, from_ in ios:
        run(name, cmdline, i, o, from_, color)


def run(
    name: str,
    cmdline: list[str],
    input_file: str,
    expected_file: str | None,
    from_: str,
    color: bool,
):
    c = util.cw(color)

    with spinner.Spinner(
        f"Running {name} with {from_} input {path.basename(input_file)} "
    ) as s:
        with open(input_file, "r") as input:
            p = subprocess.Popen(
                cmdline, stdin=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            byte_streams = p.communicate()
            exit_code = p.returncode
            stdout, stderr = [s.decode("utf-8") for s in byte_streams]

        diff = None

        if expected_file is not None:
            with open(expected_file, "r") as expected:
                diff = compare.compare_outputs(
                    stdout, expected.read(), input_file, os.isatty(sys.stdin.fileno())
                )

                s.stop(isinstance(diff, bool))

                if isinstance(diff, str):
                    print(diff)
                elif expected_file is None:
                    print(c("Input:", "yellow"))
                    with open(input_file, "r") as ifile:
                        print(util.indented(ifile.read()))
                    print(c("Got output:", "yellow"))
                    print(util.indented(stdout))
                elif diff is True:
                    print(c("NOTE: The output contained debug lines", "yellow"))

                if exit_code != 0:
                    print(
                        c(
                            f"Proccess exited with a non-zero exit code {exit_code}"
                            + (" and the following stderr:" if stderr else ""),
                            "red",
                        )
                    )

                    if stderr:
                        print(util.indented(stderr))
