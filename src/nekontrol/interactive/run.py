import os
import os.path as path
import subprocess
import sys

from .. import compare, util
from ..config import Config
from ..language import Language
from ..problems import ProblemIO
from . import spinner


def run(
    name: str,
    lang: Language,
    io: ProblemIO,
    config: Config
):
    c = util.cw(config.color)

    with spinner.Spinner(
        f"Running {name} with {io.from_} input {io.input_name()} "
    ) as s:
        with open(io.i, "r") as input_file:
            exit_code, stdout, stderr = lang.run(io.i)

        diff = None

        if config.diff and io.o is not None:
            with open(io.o, "r") as expected:
                diff = compare.compare_outputs(
                    stdout, expected.read(), io.i, os.isatty(sys.stdin.fileno())
                )

                s.stop(isinstance(diff, bool))

                if isinstance(diff, str):
                    print(diff)
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
        else:
            s.stop()

            print(c("Input:", "yellow"))
            with open(io.i, "r") as ifile:
                print(util.indented(ifile.read()))
            print(c("Got output:", "yellow"))
            print(util.indented(stdout))
