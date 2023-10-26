import difflib

from rich.markup import escape


def rich_diff_line(line: str) -> str:
    prefix, rest = line[:2], line[2:]
    match prefix:
        case "+ " | "- ":
            return f"[red]{prefix}[/red]{escape(rest)}"
        case "^ ":
            return f"[yellow]{prefix}[/yellow]{escape(rest)}"
        case _:
            return escape(line)


def diff(expected: str, actual: str) -> str | None:
    differ = difflib.Differ()

    is_diff = False

    rich_diff_lines = []
    for line in differ.compare(
        [l.rstrip() for l in expected.splitlines()],
        [l.rstrip() for l in actual.splitlines()],
    ):
        if not line[:2] == "  ":
            is_diff = True

        rich_diff_lines.append(rich_diff_line(line))

    if is_diff:
        return "\n".join(rich_diff_lines)
