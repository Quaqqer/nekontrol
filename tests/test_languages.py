import shutil
from os import path

import pytest

from nekontrol.config import Config
from nekontrol.language import (
    Cpp,
    Haskell,
    JSNode,
    Language,
    Lua,
    Python,
    RunResult,
    Rust,
)

problems_dir = path.join(path.dirname(__file__), "problems")
cfg = Config()


def language_test(lang: Language):
    with lang as runnable:
        for ifile, ofile in ins_and_outs:
            with open(ifile) as input:
                with open(ofile) as output:
                    res = runnable.run(input.read())

                    assert res == RunResult(exit=0, stdout=output.read(), stderr="")


ins_and_outs = [
    (path.join(problems_dir, "test.in"), path.join(problems_dir, "test.ans")),
    (path.join(problems_dir, "test.1.in"), path.join(problems_dir, "test.1.ans")),
    (path.join(problems_dir, "test.2.in"), path.join(problems_dir, "test.2.ans")),
]


def check_available(lang, bins):
    for binary in bins:
        if shutil.which(binary) is not None:
            return
    pytest.skip(f"no binary for {lang} is available")


def test_cpp():
    check_available("C++", ["c++"])
    language_test(Cpp(path.join(problems_dir, "test.cpp"), cfg))


def test_python():
    check_available("Python", Python.bins)
    language_test(Python(path.join(problems_dir, "test.py"), cfg))


def test_haskell():
    check_available("Haskell", ["ghc"])
    language_test(Haskell(path.join(problems_dir, "test.hs"), cfg))


def test_rust():
    check_available("Rust", ["rustc"])
    language_test(Rust(path.join(problems_dir, "test.rs"), cfg))


def test_lua():
    check_available("Lua", Lua.bins)
    language_test(Lua(path.join(problems_dir, "test.lua"), cfg))


def test_node():
    check_available("Node", JSNode.bins)
    language_test(JSNode(path.join(problems_dir, "test.js"), cfg))
