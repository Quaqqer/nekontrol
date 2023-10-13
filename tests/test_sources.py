from os import path

from nekontrol.config import Config
from nekontrol.problems.sample import ProblemSample
from nekontrol.problems.sources.kattis import KattisSource
from nekontrol.problems.sources.local import LocalSource


def test_local():
    samples = LocalSource().find_problem(
        "test",
        source_dir=path.join(path.dirname(__file__), "problems"),
        cfg=Config(),
    )

    assert (
        ProblemSample(name="test.1.in", source="Local", input="2\n", output="4\n")
        in samples
    )

    assert (
        ProblemSample(name="test.in", source="Local", input="1\n", output="2\n")
        in samples
    )

    assert (
        ProblemSample(name="test.2.in", source="Local", input="3\n", output="6\n")
        in samples
    )

    assert len(samples) == 3


def test_kattis():
    samples = KattisSource().find_uncached("ovissa", "", cfg=Config())

    assert (
        ProblemSample(name="1.in", source="Kattis", input="uuuuu\n", output="5\n")
        in samples
    )

    assert (
        ProblemSample(
            name="2.in", source="Kattis", input="uuuuuuuuuuuuuu\n", output="14\n"
        )
        in samples
    )

    assert len(samples) == 2
