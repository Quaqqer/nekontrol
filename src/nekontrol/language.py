import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from os import path
from typing import Callable, Union, assert_never

from click import ClickException

from nekontrol.interactive.tasks import TaskContext

from . import util
from .config import Config


@dataclass
class RunResult:
    exit: int
    stdout: str
    stderr: str


@dataclass
class CompileOk:
    pass


@dataclass
class CompileError:
    exit: int
    stderr: str


CompileResult = Union[CompileOk, CompileError]


class Runnable:
    def __init__(self, run: Callable[[str], RunResult]):
        self._run = run

    def run(self, input_file: str) -> RunResult:
        return self._run(input_file)


class Language:
    def __init__(
        self, source_file: str, config: Config, tctx: TaskContext | None = None
    ):
        self.source_file = source_file
        self.config = config
        self.tctx = tctx

    def prepare(self) -> Runnable:
        raise NotImplementedError()

    def cleanup(self):
        pass

    @property
    def full_name(self) -> str:
        raise NotImplementedError()

    def __enter__(self) -> Runnable:
        return self.prepare()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class InterpretedLanguage(Language):
    @property
    def bins(self) -> list[str]:
        raise NotImplementedError()

    def __init__(
        self, source_file: str, config: Config, tctx: TaskContext | None = None
    ):
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
    def full_name(self) -> str:
        return "Python 3"

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
    def full_name(self) -> str:
        return "Lua"

    @property
    def bins(self):
        return ["lua", "luajit"]


class JSNode(InterpretedLanguage):
    @property
    def full_name(self) -> str:
        return "Node"

    @property
    def bins(self):
        return ["node"]


class CompiledLanguage(Language):
    @property
    def cmdline(self) -> list[str]:
        raise NotImplementedError()

    def prepare(self) -> Runnable:
        task = (
            self.tctx.add_task(f"Compiling {self.source_file} ") if self.tctx else None
        )

        self.compiled_output = tempfile.mktemp()
        compile_result = self.compile()

        match compile_result:
            case CompileOk():
                if task:
                    task.ok()

                return Runnable(lambda i: generic_run([self.compiled_output], i))
            case CompileError(exit, stderr):
                if task:
                    task.fail()

                err_msg = f"Compilation exited with code {exit}" + (
                    " and stderr:\n" + util.indented(stderr) if stderr else ""
                )
                raise ClickException(err_msg)
            case _:
                assert_never(compile_result)

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
    def full_name(self) -> str:
        return "C++"

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
    def full_name(self) -> str:
        return "Rust"

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
    @property
    def full_name(self) -> str:
        return "Haskell"

    def prepare(self):
        self.temp_out_dir = tempfile.mkdtemp()
        return super().prepare()

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


def get_lang(
    source_file: str, config: Config, tctx: TaskContext | None = None
) -> Language | None:
    _, ext = path.splitext(source_file)
    match ext:
        case ".cc" | ".cpp" | ".cxx" | ".c++":
            return Cpp(source_file, config, tctx=tctx)
        case ".py":
            return Python(source_file, config, tctx=tctx)
        case ".hs":
            return Haskell(source_file, config, tctx=tctx)
        case ".rs":
            return Rust(source_file, config, tctx=tctx)
        case ".lua":
            return Lua(source_file, config, tctx=tctx)
        case ".js":
            return JSNode(source_file, config, tctx=tctx)
        case _:
            return None


def generic_run(cmdline: list[str], input: str) -> RunResult:
    p = subprocess.Popen(
        cmdline,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    byte_streams = p.communicate(input=input.encode("utf-8"))
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
