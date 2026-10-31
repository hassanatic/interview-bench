from __future__ import annotations

import argparse
import json

from .grader import grade, render_markdown
from .problems import PROBLEMS


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="interview-bench", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="show the available problems and their parts")
    grade_cmd = sub.add_parser("grade", help="grade a solution file against a problem's hidden cases")
    grade_cmd.add_argument("problem")
    grade_cmd.add_argument("solution")
    grade_cmd.add_argument("--timeout", type=float, default=2.0, help="seconds allowed per case (default 2)")
    grade_cmd.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    if args.command == "list":
        for problem in PROBLEMS.values():
            print(f"{problem.id}: {problem.title}")
            for part in problem.parts:
                print(f"  part {part.number} `{part.function}`: {part.prompt}")
        return 0

    report = grade(args.problem, args.solution, timeout=args.timeout)
    print(json.dumps(report.to_dict(), indent=2) if args.json else render_markdown(report), end="")
    return 0 if report.solved == len(report.parts) else 1
