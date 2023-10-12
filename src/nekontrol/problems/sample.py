from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemSample:
    """A sample for a problem.

    Contains the input data and maybe also the expected output
    """

    name: str
    """The name of the source"""
    source: str
    """An explaining source for the problem sample"""
    input: str
    """The input data"""
    output: str | None
    """The output data"""
