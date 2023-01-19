import difflib

import termcolor

from . import util


def compare_outputs(
    output: str, expected_output: str, input_file: str, colors: bool
) -> str | None:
    differ = difflib.Differ()
    diff = list(
        differ.compare(
            list(map(str.rstrip, expected_output.splitlines())),
            list(map(str.rstrip, output.splitlines())),
        )
    )

    def colored(s, *args):
        if colors:
            return termcolor.colored(s, *args)
        else:
            return s

    if all(d.startswith("  ") for d in diff):
        return None
    else:
        with open(input_file, "r") as ifile:
            return (
                colored("Input:", "yellow")
                + "\n"
                + util.indented(ifile.read())
                + "\n"
                + colored("Diff:", "yellow")
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
