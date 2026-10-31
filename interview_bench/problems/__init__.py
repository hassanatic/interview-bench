from ..problem import Problem
from . import intervals, request_logs

PROBLEMS: dict[str, Problem] = {p.id: p for p in (request_logs.PROBLEM, intervals.PROBLEM)}


def get_problem(problem_id: str) -> Problem:
    try:
        return PROBLEMS[problem_id]
    except KeyError:
        raise KeyError(f"unknown problem '{problem_id}', try: {', '.join(PROBLEMS)}") from None
