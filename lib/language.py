import subprocess
import tempfile


def extension_lang(extension: str) -> str | None:

    match extension:
        case ".cc" | ".cpp" | ".cxx":
            return "c++"
        case ".py":
            return "python"
        case ".hs":
            return "haskell"
        case _:
            return None


def is_compiled(lang: str):
    return lang in {"c++", "haskell"}


def script_cmdline(lang: str, file_path: str) -> list[str]:
    match lang:
        case "python":
            return ["pypy3", file_path]

        case _:
            raise NotImplemented("Unknown language")


def compile(file: str, language: str, output_file: str, color: bool) -> None | str:
    match language:
        case "haskell":
            with tempfile.TemporaryDirectory() as tempdir:
                return compile_generic(
                    [
                        "ghc",
                        "-outputdir",
                        tempdir,
                        file,
                        "-o",
                        output_file,
                    ]
                )

        case "c++":
            return compile_generic(
                [
                    "c++",
                    "--std=c++17",
                    file,
                    "-o",
                    output_file,
                    f"-fdiagnostics-color={'always' if color else 'never'}",
                ]
            )

        case _:
            raise NotImplemented("Unknown language")


def compile_generic(cmdline: list[str]) -> None | str:
    p = subprocess.Popen(cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return_code = p.wait()

    if return_code == 0:
        return
    else:
        assert p.stderr
        return p.stderr.read().decode("utf-8")
