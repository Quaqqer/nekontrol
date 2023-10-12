import time

from .. import compare, util
from ..config import Config
from ..language import Runnable
from ..problems.sample import ProblemSample
from . import spinner


def run(name: str, runnable: Runnable, sample: ProblemSample, config: Config):
    c = util.cw(config.color)

    with spinner.Spinner(
        f"Running {name} with {sample.source} input {sample.name} ",
        color=config.color,
        newline=False,
    ) as s:
        start = time.time()
        result = runnable.run(sample.input)
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

        if config.diff and sample.output is not None:
            diff = compare.compare_outputs(
                result.stdout, sample.output, sample.input, config
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
            print(util.indented(sample.input))
            print(c("Got output:", "yellow"))
            print(util.indented(result.stdout))

        if result.stderr:
            print(c("Got stderr:", "yellow"))
            print(util.indented(result.stderr))
