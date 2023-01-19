import difflib
import re

import termcolor

from . import util

debug_regex = re.compile("^(?:debug|dbg)", re.IGNORECASE)


def compare_outputs(
    output: str, expected_output: str, input_file: str, colors: bool, ignore_debug=True
) -> str | bool:
    c = util.cw(colors)

    output_lines = []
    found_debug = False
    if ignore_debug:
        for line in output.splitlines():
            if debug_regex.match(line):
                found_debug = True
            else:
                output_lines.append(line)
    else:
        output_lines = output.splitlines()

    output_lines = (
        list(filter(lambda line: not debug_regex.match(line), output.splitlines()))
        if ignore_debug
        else output.splitlines()
    )

    differ = difflib.Differ()
    diff = list(
        differ.compare(
            list(map(str.rstrip, expected_output.splitlines())),
            list(map(str.rstrip, output_lines)),
        )
    )

    if all(d.startswith("  ") for d in diff):
        return found_debug
    else:
        with open(input_file, "r") as ifile:
            return (
                c("Input:", "yellow")
                + "\n"
                + util.indented(ifile.read())
                + "\n"
                + c("Diff:", "yellow")
                + "\n"
                + "\n".join(color_diff(diff) if colors else diff)
            )


def color_diff(diff: list[str]) -> list[str]:
    def color_line(line: str) -> str:
        match line[0:2]:
            case "+ " | "- " as start:
                return termcolor.colored(start, on_color="on_red") + line[2:]
            case "? " as start:
                return termcolor.colored(start, on_color="on_yellow") + line[2:]
            case _:
                return line

    return list(map(color_line, diff))
