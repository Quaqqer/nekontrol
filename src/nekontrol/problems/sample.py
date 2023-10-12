from dataclasses import dataclass
from typing import Any


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

    @staticmethod
    def from_json(obj: Any) -> "ProblemSample":
        name = obj["name"]
        source = obj["source"]
        input = obj["input"]
        output = obj["output"]
        assert all(isinstance(v, str) for v in [name, source, input, output])
        return ProblemSample(name=name, source=source, input=input, output=output)

    def to_json(self) -> Any:
        return {
            "name": self.name,
            "source": self.source,
            "input": self.input,
            "output": self.output,
        }
