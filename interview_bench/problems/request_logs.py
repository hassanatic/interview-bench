"""Request logs: three parts that build on each other, the usual interview shape.

Each log line is "<unix seconds> <user> <method> <path> <status>". Lines are not
guaranteed to be in time order.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict, deque

from ..problem import Case, Part, Problem

SAMPLE = [
    "100 alice GET /home 200",
    "101 bob GET /home 200",
    "102 alice POST /login 302",
    "105 carol GET /docs 200",
    "106 alice GET /home 200",
    "160 bob GET /api 500",
]


def _parse(lines):
    for line in lines:
        ts, user, *_ = line.split()
        yield int(ts), user


def ref_count_by_user(lines):
    return dict(Counter(user for _, user in _parse(lines)))


def ref_top_users(lines, k):
    counts = ref_count_by_user(lines)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [user for user, _ in ranked[:k]]


def ref_rate_limited_users(lines, limit, window):
    stamps_by_user = defaultdict(list)
    for ts, user in _parse(lines):
        stamps_by_user[user].append(ts)

    flagged = []
    for user, stamps in stamps_by_user.items():
        stamps.sort()
        recent = deque()
        for ts in stamps:
            recent.append(ts)
            while recent[0] <= ts - window:
                recent.popleft()
            if len(recent) > limit:
                flagged.append(user)
                break
    return sorted(flagged)


def _big_log(seed=7, n=100_000, users=50, bursts=3):
    rng = random.Random(seed)
    names = [f"user{i:02d}" for i in range(users)]
    lines = [f"{rng.randrange(0, 86_400)} {rng.choice(names)} GET /api 200" for _ in range(n)]
    for name in rng.sample(names, bursts):
        start = rng.randrange(0, 86_000)
        lines += [f"{start + rng.randrange(0, 20)} {name} GET /api 429" for _ in range(30)]
    rng.shuffle(lines)
    return lines


def _case(name, category, args_fn, ref):
    def make():
        args = args_fn()
        return args, ref(*args)

    return Case(name, category, make)


PROBLEM = Problem(
    id="request-logs",
    title="Request logs: counts, top users, rate limiting",
    parts=(
        Part(
            1,
            "count_by_user",
            "Return a dict mapping each user to their number of requests.",
            (
                _case("sample", "basic", lambda: (SAMPLE,), ref_count_by_user),
                _case("empty log", "edge", lambda: ([],), ref_count_by_user),
                _case("one user only", "edge", lambda: (["5 zed GET / 200"] * 3,), ref_count_by_user),
                _case("100k lines", "large", lambda: (_big_log(),), ref_count_by_user),
            ),
        ),
        Part(
            2,
            "top_users",
            "Return the k users with the most requests, ties broken by name A to Z.",
            (
                _case("sample, k=2", "basic", lambda: (SAMPLE, 2), ref_top_users),
                _case(
                    "ties sorted by name",
                    "edge",
                    lambda: (["1 bob GET / 200", "2 amy GET / 200", "3 cat GET / 200"], 2),
                    ref_top_users,
                ),
                _case("k larger than user count", "edge", lambda: (SAMPLE, 10), ref_top_users),
                _case("100k lines, k=5", "large", lambda: (_big_log(), 5), ref_top_users),
            ),
        ),
        Part(
            3,
            "rate_limited_users",
            "Return, sorted, the users who ever make more than `limit` requests in a window: "
            "two requests share a window when their timestamps differ by less than `window` seconds.",
            (
                _case("sample, limit=2, window=10", "basic", lambda: (SAMPLE, 2, 10), ref_rate_limited_users),
                _case(
                    "requests exactly one window apart",
                    "edge",
                    lambda: (["0 amy GET / 200", "60 amy GET / 200", "120 amy GET / 200"], 1, 60),
                    ref_rate_limited_users,
                ),
                _case(
                    "lines out of time order",
                    "edge",
                    lambda: (["50 amy GET / 200", "10 amy GET / 200", "30 amy GET / 200"], 2, 45),
                    ref_rate_limited_users,
                ),
                _case("100k lines with bursts", "large", lambda: (_big_log(), 12, 60), ref_rate_limited_users),
            ),
        ),
    ),
)
