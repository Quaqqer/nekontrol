import time

from .. import compare, util
from ..config import Config
from ..language import Runnable
from ..problems import ProblemIO
from . import spinner


def run(name: str, runnable: Runnable, io: ProblemIO, config: Config):
    c = util.cw(config.color)

    with spinner.Spinner(
        f"Running {name} with {io.from_} input {io.input_name()} ",
        color=config.color,
        newline=False,
    ) as s:
        start = time.time()
        result = runnable.run(io.i)
        finish = time.time()
        duration = finish - start

        if duration < 1:
            time_color_args = dict(color="black", on_color="on_green")
        elif duration < 3:
            time_color_args = dict(color="black", on_color="on_yellow")
        else:
            time_color_args = dict(color="black", on_color="on_red")
        time_msg = " " + c(f" ⏱  {duration:.3} s", **time_color_args)

        diff = None

        if config.diff and io.o is not None:
            with open(io.o, "r") as expected:
                diff = compare.compare_outputs(
                    result.stdout, expected.read(), io.i, config
                )

                if isinstance(diff, bool):
                    s.ok()
                else:
                    s.fail()
                print(time_msg)

                if isinstance(diff, str):
                    print(diff)
                elif diff is True:
                    print(c("NOTE: The output contained debug lines", "yellow"))

                if result.exit != 0:
                    print(
                        c(
                            f"Proccess exited with a non-zero exit code {result.exit}"
                            + (" and the following stderr:" if result.stderr else ""),
                            "red",
                        )
                    )

                    if result.stderr:
                        print(util.indented(result.stderr))
                    return
        else:
            s.stop()
            print(time_msg)

            print(c("Input:", "yellow"))
            with open(io.i, "r") as ifile:
                print(util.indented(ifile.read()))
            print(c("Got output:", "yellow"))
            print(util.indented(result.stdout))

        if result.stderr:
            print(c("Got stderr:", "yellow"))
            print(util.indented(result.stderr))
