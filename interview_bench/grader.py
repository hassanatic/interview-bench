"""Run a candidate's solution file against every hidden case of a problem.

Each case runs in its own process. That isolates the candidate's code (a crash or
sys.exit cannot take the grader down) and lets a slow solution be stopped cleanly
when it runs past the time limit, which is how "correct but quadratic" shows up.
"""
from __future__ import annotations

import importlib.util
import multiprocessing as mp
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .problems import get_problem

# Building a large input (and its expected answer) happens before the clock starts.
SETUP_TIMEOUT = 60.0


@dataclass
class CaseResult:
    part: int
    case: str
    category: str
    status: str  # passed | failed | timeout | error | missing
    seconds: float | None = None
    detail: str = ""


@dataclass
class PartReport:
    number: int
    function: str
    verdict: str
    cases: list[CaseResult] = field(default_factory=list)


@dataclass
class Report:
    problem: str
    candidate: str
    parts: list[PartReport]

    @property
    def solved(self) -> int:
        return sum(p.verdict == "solved" for p in self.parts)

    def to_dict(self) -> dict:
        return {"problem": self.problem, "candidate": self.candidate, "solved": self.solved,
                "parts": [asdict(p) for p in self.parts]}


def _short(value, limit=120):
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _load(path):
    spec = importlib.util.spec_from_file_location("candidate_solution", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _worker(conn, candidate_path, problem_id, part_no, case_index):
    try:
        part = get_problem(problem_id).part(part_no)
        args, expected = part.cases[case_index].make()
        fn = getattr(_load(candidate_path), part.function, None)
        conn.send(("ready",))
        if fn is None:
            conn.send(("missing", f"no function named {part.function}"))
            return
        start = time.perf_counter()
        got = fn(*args)
        elapsed = time.perf_counter() - start
        try:
            ok = part.compare(got, expected)
        except Exception:
            ok = False
        if ok:
            conn.send(("passed", elapsed, ""))
        else:
            conn.send(("failed", elapsed, f"expected {_short(expected)}, got {_short(got)}"))
    except Exception as exc:
        conn.send(("error", f"{type(exc).__name__}: {exc}"))
    finally:
        conn.close()


def _final(message):
    status = message[0]
    if status in ("passed", "failed"):
        return status, message[1], message[2]
    return status, None, message[1]


def run_case(candidate_path, problem_id, part_no, case_index, timeout):
    ctx = mp.get_context("spawn")
    receiver, sender = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_worker, args=(sender, candidate_path, problem_id, part_no, case_index), daemon=True)
    proc.start()
    sender.close()
    try:
        if not receiver.poll(SETUP_TIMEOUT):
            return "error", None, "setup did not finish"
        first = receiver.recv()
        if first[0] != "ready":
            return _final(first)
        if not receiver.poll(timeout):
            return "timeout", None, f"no answer within {timeout:g}s"
        return _final(receiver.recv())
    except EOFError:
        return "error", None, "the solution exited without returning an answer"
    finally:
        if proc.is_alive():
            proc.kill()
        proc.join()
        receiver.close()


def _verdict(results: list[CaseResult]) -> str:
    statuses = [r.status for r in results]
    if all(s == "missing" for s in statuses):
        return "not attempted"
    if all(s == "passed" for s in statuses):
        return "solved"
    small = [r for r in results if r.category != "large"]
    large = [r for r in results if r.category == "large"]
    if all(r.status == "passed" for r in small) and any(r.status == "timeout" for r in large):
        return "correct but too slow at scale"
    if any(r.status == "passed" and r.category == "basic" for r in results):
        return "partial"
    return "not solved"


def grade(problem_id: str, solution_path: str | Path, timeout: float = 2.0) -> Report:
    problem = get_problem(problem_id)
    path = str(Path(solution_path).resolve())
    parts = []
    for part in problem.parts:
        results = []
        for index, case in enumerate(part.cases):
            status, seconds, detail = run_case(path, problem.id, part.number, index, timeout)
            results.append(CaseResult(part.number, case.name, case.category, status, seconds, detail))
        parts.append(PartReport(part.number, part.function, _verdict(results), results))
    return Report(problem.id, Path(solution_path).name, parts)


def render_markdown(report: Report) -> str:
    lines = [
        f"# {report.problem}: {report.solved} of {len(report.parts)} parts solved",
        "",
        f"Candidate file: `{report.candidate}`",
        "",
        "| Part | Function | Verdict | basic | edge | large |",
        "|---|---|---|---|---|---|",
    ]
    notes = []
    for part in report.parts:
        cells = []
        for category in ("basic", "edge", "large"):
            cases = [c for c in part.cases if c.category == category]
            passed = sum(c.status == "passed" for c in cases)
            cells.append(f"{passed}/{len(cases)}")
        lines.append(f"| {part.number} | `{part.function}` | {part.verdict} | " + " | ".join(cells) + " |")
        for case in part.cases:
            if case.status != "passed":
                notes.append(f"- Part {part.number}, {case.category} case \"{case.case}\": {case.status}. {case.detail}".rstrip())
    if notes:
        lines += ["", "## What failed", "", *notes]
    return "\n".join(lines) + "\n"
