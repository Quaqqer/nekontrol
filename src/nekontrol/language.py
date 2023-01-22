import subprocess
import tempfile

from . import config


def extension_lang(extension: str) -> str | None:

    match extension:
        case ".cc" | ".cpp" | ".cxx":
            return "c++"
        case ".py":
            return "python"
        case ".hs":
            return "haskell"
        case ".rs":
            return "rust"
        case _:
            return None


def is_compiled(lang: str):
    return lang in {"c++", "haskell", "rust"}


def script_cmdline(lang: str, file_path: str) -> list[str]:
    match lang:
        case "python":
            return ["pypy3", file_path]

        case _:
            raise NotImplemented("Unknown language")


def compile(
    file: str, language: str, output_file: str, color: bool, cfg: config.Config
) -> None | str:
    match language:
        case "haskell":
            with tempfile.TemporaryDirectory() as tempdir:
                cmdline = [
                    "ghc",
                    "-outputdir",
                    tempdir,
                    file,
                    "-o",
                    output_file,
                ]
                return compile_generic(cmdline)

        case "c++":
            cmdline = [
                "c++",
                "--std=c++17",
                file,
                "-o",
                output_file,
                f"-fdiagnostics-color={'always' if color else 'never'}",
            ]

            if cfg.cpp_libs_dir is not None:
                cmdline += [f"-I{cfg.cpp_libs_dir}"]

            return compile_generic(cmdline)

        case "rust":
            cmdline = [
                "rustc",
                "-O",
                "--crate-type",
                "bin",
                "--edition=2018",
                file,
                "--color",
                "always" if color else "never",
                "-o",
                output_file,
            ]
            return compile_generic(cmdline)

        case _:
            raise NotImplemented("Unknown language")


def compile_generic(cmdline: list[str]) -> None | str:
    p = subprocess.Popen(cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert p.stderr
    _, errbytes = p.communicate()
    return_code = p.wait()

    if return_code == 0:
        return
    else:
        return errbytes.decode("utf-8")
