from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


def exact(got: Any, expected: Any) -> bool:
    return got == expected


@dataclass(frozen=True)
class Case:
    """One hidden test. `make` builds the arguments and the expected answer inside
    the worker process, so large inputs never have to be pickled across processes."""

    name: str
    category: str  # basic | edge | large
    make: Callable[[], tuple[tuple, Any]]


@dataclass(frozen=True)
class Part:
    number: int
    function: str
    prompt: str
    cases: tuple[Case, ...]
    compare: Callable[[Any, Any], bool] = exact


@dataclass(frozen=True)
class Problem:
    id: str
    title: str
    parts: tuple[Part, ...]

    def part(self, number: int) -> Part:
        for part in self.parts:
            if part.number == number:
                return part
        raise KeyError(f"{self.id} has no part {number}")
