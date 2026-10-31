"""Intervals: merging, covered length and meeting rooms.

Intervals are [start, end) pairs of integers with start < end, in any order.
"""
from __future__ import annotations

import random

from ..problem import Case, Part, Problem


def ref_merge(intervals):
    merged = []
    for start, end in sorted(tuple(i) for i in intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def ref_covered_length(intervals):
    return sum(end - start for start, end in ref_merge(intervals))


def ref_min_rooms(meetings):
    # At equal times an end (-1) sorts before a start (+1), so back-to-back meetings share a room.
    events = sorted([(start, 1) for start, _ in meetings] + [(end, -1) for _, end in meetings])
    rooms = best = 0
    for _, delta in events:
        rooms += delta
        best = max(best, rooms)
    return best


def as_pairs(got, expected):
    return [tuple(x) for x in got] == [tuple(x) for x in expected]


def _big(seed=11, n=100_000):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        start = rng.randrange(0, 10_000_000)
        out.append([start, start + rng.randrange(1, 500)])
    return out


def _case(name, category, args_fn, ref):
    def make():
        args = args_fn()
        return args, ref(*args)

    return Case(name, category, make)


SAMPLE = [[1, 3], [8, 10], [2, 6], [15, 18]]

PROBLEM = Problem(
    id="intervals",
    title="Intervals: merge, covered length, meeting rooms",
    parts=(
        Part(
            1,
            "merge",
            "Merge overlapping or touching intervals and return them sorted by start.",
            (
                _case("sample", "basic", lambda: (SAMPLE,), ref_merge),
                _case("touching intervals", "edge", lambda: ([[1, 3], [3, 5]],), ref_merge),
                _case("one inside another", "edge", lambda: ([[1, 10], [2, 3], [4, 5]],), ref_merge),
                _case("100k intervals", "large", lambda: (_big(),), ref_merge),
            ),
            compare=as_pairs,
        ),
        Part(
            2,
            "covered_length",
            "Return the total length covered by at least one interval.",
            (
                _case("sample", "basic", lambda: (SAMPLE,), ref_covered_length),
                _case("no intervals", "edge", lambda: ([],), ref_covered_length),
                _case("duplicates", "edge", lambda: ([[0, 5], [0, 5], [1, 2]],), ref_covered_length),
                _case("100k intervals", "large", lambda: (_big(),), ref_covered_length),
            ),
        ),
        Part(
            3,
            "min_rooms",
            "Return the minimum number of rooms needed to hold all meetings.",
            (
                _case("sample", "basic", lambda: (SAMPLE,), ref_min_rooms),
                _case("back-to-back share a room", "edge", lambda: ([[0, 30], [30, 60], [60, 90]],), ref_min_rooms),
                _case("all overlap", "edge", lambda: ([[0, 10], [1, 11], [2, 12]],), ref_min_rooms),
                _case("100k meetings", "large", lambda: (_big(),), ref_min_rooms),
            ),
        ),
    ),
)
