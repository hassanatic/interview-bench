import json

from interview_bench.cli import main
from interview_bench.grader import grade, render_markdown

from conftest import CANDIDATES


def verdicts(report):
    return {p.number: p.verdict for p in report.parts}


def test_correct_solution_solves_every_part():
    report = grade("request-logs", CANDIDATES / "logs_good.py")
    assert verdicts(report) == {1: "solved", 2: "solved", 3: "solved"}
    assert report.solved == 3


def test_quadratic_solution_is_correct_but_too_slow_at_scale():
    report = grade("request-logs", CANDIDATES / "logs_quadratic.py", timeout=1.0)
    assert verdicts(report) == {1: "solved", 2: "solved", 3: "correct but too slow at scale"}
    large = [c for c in report.parts[2].cases if c.category == "large"][0]
    assert large.status == "timeout"


def test_missing_tie_break_is_partial_and_unwritten_part_is_not_attempted():
    report = grade("request-logs", CANDIDATES / "logs_buggy.py")
    assert verdicts(report)[1] == "solved"
    assert verdicts(report)[2] == "partial"
    tie = [c for c in report.parts[1].cases if c.case == "ties sorted by name"][0]
    assert tie.status == "failed" and "['amy', 'bob']" in tie.detail
    assert verdicts(report)[3] == "not attempted"


def test_off_by_one_on_boundaries_is_caught_by_edge_cases():
    report = grade("intervals", CANDIDATES / "intervals_touching_bug.py")
    assert verdicts(report)[1] == "partial"
    assert verdicts(report)[3] == "partial"
    failed = {c.case for p in report.parts for c in p.cases if c.status == "failed"}
    assert "touching intervals" in failed and "back-to-back share a room" in failed


def test_exceptions_and_exits_are_reported_not_fatal():
    report = grade("intervals", CANDIDATES / "crashes.py")
    merge_cases = report.parts[0].cases
    assert all(c.status == "error" and "ValueError" in c.detail for c in merge_cases)
    assert all(c.status == "error" for c in report.parts[1].cases)
    assert verdicts(report)[3] == "not attempted"


def test_markdown_report_lists_what_failed():
    text = render_markdown(grade("request-logs", CANDIDATES / "logs_buggy.py"))
    assert "1 of 3 parts solved" in text
    assert 'edge case "ties sorted by name": failed' in text


def test_cli_exit_code_and_json(capsys):
    assert main(["grade", "request-logs", str(CANDIDATES / "logs_good.py"), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["solved"] == 3
    assert main(["grade", "intervals", str(CANDIDATES / "crashes.py")]) == 1
