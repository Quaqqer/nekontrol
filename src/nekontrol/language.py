import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from os import path
from typing import Callable

from click import ClickException

from . import util
from .config import Config
from .interactive.spinner import Spinner


@dataclass
class RunResult:
    exit: int
    stdout: str
    stderr: str


@dataclass
class CompileResult:
    pass


@dataclass
class CompileOk(CompileResult):
    pass


@dataclass
class CompileError(CompileResult):
    exit: int
    stderr: str


class Runnable:
    def __init__(self, run: Callable[[str], RunResult]):
        self._run = run

    def run(self, input_file: str) -> RunResult:
        return self._run(input_file)


class Language:
    def __init__(self, source_file: str, config: Config):
        self.source_file = source_file
        self.config = config

    def prepare(self) -> Runnable:
        raise NotImplementedError()

    def cleanup(self):
        pass

    def __enter__(self) -> Runnable:
        return self.prepare()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class InterpretedLanguage(Language):
    @property
    def bins(self) -> list[str]:
        raise NotImplementedError()

    def __init__(self, source_file: str, config: Config):
        super().__init__(source_file, config)
        bin = find_bin(self.bins)

        if bin is None:
            raise Exception(
                f"Binary for language not found, needs one of {', '.join(self.bins)}"
            )

        self.bin = bin

    def prepare(self) -> Runnable:
        return Runnable(run=lambda i: generic_run([self.bin, self.source_file], i))


class Python(InterpretedLanguage):
    @property
    def bins(self) -> list[str]:
        return [
            "pypy38",
            "pypy3.8",
            "pypy3",
            "python38",
            "python3.8",
            "python3",
            "python",
        ]


class Lua(InterpretedLanguage):
    @property
    def bins(self):
        return ["lua", "luajit"]


class JSNode(InterpretedLanguage):
    @property
    def bins(self):
        return ["node"]


class CompiledLanguage(Language):
    @property
    def cmdline(self) -> list[str]:
        raise NotImplementedError()

    def prepare(self) -> Runnable:
        with Spinner(f"Compiling {self.source_file} ", color=self.config.color) as s:
            self.compiled_output = tempfile.mktemp()
            compile_result = self.compile()

            match compile_result:
                case CompileOk():
                    s.stop()
                    return Runnable(lambda i: generic_run([self.compiled_output], i))
                case CompileError(exit, stderr):
                    s.stop()
                    err_msg = f"Compilation exited with code {exit}" + (
                        " and stderr:\n" + util.indented(stderr) if stderr else ""
                    )
                    raise ClickException(err_msg)
                case _:
                    raise AssertionError("Unreachable")

    def cleanup(self):
        if path.exists(self.compiled_output):
            os.remove(self.compiled_output)

    def run(self, input_file: str):
        return generic_run([self.compiled_output], input_file)

    def compile(self) -> CompileResult:
        """Compile the file.

        Returns:
            Nothing if successful, the exit code and the stderr if the exit
            code was non-0.
        """
        p = subprocess.Popen(
            self.cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )
        _, stderr = p.communicate()
        exit_code = p.returncode

        if exit_code == 0:
            return CompileOk()
        else:
            return CompileError(exit=exit_code, stderr=stderr.decode("utf-8"))


class Cpp(CompiledLanguage):
    @property
    def cmdline(self) -> list[str]:
        cmdline = [
            "c++",
            "--std=c++17",
            self.source_file,
            "-o",
            self.compiled_output,
            f"-fdiagnostics-color={'always' if self.config.color else 'never'}",
        ]

        if self.config.cpp_libs_dir is not None:
            cpp_sources = []
            for root, _, files in os.walk(self.config.cpp_libs_dir):
                for file in files:
                    _, ext = path.splitext(file)
                    if ext in {".cc", ".cpp", ".cxx"}:
                        cpp_sources.append(path.join(root, file))

            cmdline += [f"-I{self.config.cpp_libs_dir}"] + cpp_sources

        return cmdline


class Rust(CompiledLanguage):
    @property
    def cmdline(self):
        return [
            "rustc",
            "-O",
            "--crate-type",
            "bin",
            "--edition=2018",
            self.source_file,
            "--color",
            "always" if self.config.color else "never",
            "-o",
            self.compiled_output,
        ]


class Haskell(CompiledLanguage):
    def prepare(self):
        self.temp_out_dir = tempfile.mkdtemp()
        super().prepare()

    def cleanup(self):
        super().cleanup()
        shutil.rmtree(self.temp_out_dir)

    @property
    def cmdline(self):
        return [
            "ghc",
            "-outputdir",
            self.temp_out_dir,
            self.source_file,
            "-o",
            self.compiled_output,
        ]


def get_lang(source_file: str, config: Config) -> Language | None:
    _, ext = path.splitext(source_file)
    match ext:
        case ".cc" | ".cpp" | ".cxx":
            return Cpp(source_file, config)
        case ".py":
            return Python(source_file, config)
        case ".hs":
            return Haskell(source_file, config)
        case ".rs":
            return Rust(source_file, config)
        case ".lua":
            return Lua(source_file, config)
        case ".js":
            return JSNode(source_file, config)
        case _:
            return None


def generic_run(cmdline: list[str], input_file: str) -> RunResult:
    with open(input_file, "r") as input:
        p = subprocess.Popen(
            cmdline,
            stdin=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        byte_streams = p.communicate()
        exit_code = p.returncode
        stdout, stderr = [s.decode("utf-8") for s in byte_streams]
        return RunResult(exit=exit_code, stdout=stdout, stderr=stderr)


def find_bin(options: list[str]) -> str | None:
    for option in options:
        path = shutil.which(option)
        if path is not None:
            return path
    return None


def compile_generic(cmdline: list[str]) -> None | str:
    p = subprocess.Popen(cmdline, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert p.stderr
    _, errbytes = p.communicate()
    return_code = p.wait()

    if return_code == 0:
        return
    else:
        return errbytes.decode("utf-8")
