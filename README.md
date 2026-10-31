# interview-bench

A small grader for multi-part coding interview problems, the format where a candidate solves part 1,
then extends it in part 2 and part 3. It runs a candidate's solution file against hidden cases and
writes a short rubric report: which parts are solved, which categories of case failed, and why.

```bash
pip install -e .
interview-bench list
interview-bench grade request-logs solution.py            # markdown report, exit 1 unless every part is solved
interview-bench grade intervals solution.py --json --timeout 3
```

```
# request-logs: 2 of 3 parts solved

| Part | Function | Verdict | basic | edge | large |
|---|---|---|---|---|---|
| 1 | `count_by_user` | solved | 1/1 | 2/2 | 1/1 |
| 2 | `top_users` | solved | 1/1 | 2/2 | 1/1 |
| 3 | `rate_limited_users` | correct but too slow at scale | 1/1 | 2/2 | 0/1 |

## What failed

- Part 3, large case "100k lines with bursts": timeout. no answer within 1s
```

## How it grades

Every part has hidden cases in three categories:

- **basic**: the worked example from the prompt
- **edge**: the boundaries people get wrong (empty input, ties, touching intervals, requests exactly one
  window apart, unsorted input)
- **large**: 100k-row inputs with a per-case time limit, which separates a linear or n log n solution
  from a quadratic one without having to read the code

Each case runs in its own process, so a solution that crashes, calls `sys.exit` or loops forever is
reported as an error or a timeout instead of taking the grader down. Inputs and expected answers are
built inside that process from a reference solution, and the clock starts only when the candidate's
function is called.

Verdicts per part: `solved`, `correct but too slow at scale`, `partial` (the basic case passes, something
else does not), `not solved`, `not attempted` (function missing).

## Problems

- **request-logs**: count requests per user, top-k users with a tie-break, and users who break a
  sliding-window rate limit.
- **intervals**: merge intervals, total covered length, and the minimum number of meeting rooms.

Adding a problem means writing a reference solution and a list of cases; see
`interview_bench/problems/request_logs.py`.

## Tests

```bash
pip install -e ".[test]" && pytest -q
```

The tests grade sample candidate files in `tests/candidates/`: a correct one, a correct but quadratic
one, one with a missing tie-break and an unwritten part, one with boundary bugs, and one that raises and
exits. Each must get the verdict a human reviewer would give it.

## Limits

The time limit is a heuristic for complexity, not a proof, and the grader runs candidate code without a
sandbox, so only run files you trust. It checks correctness and scale; communication, code style and
problem-solving approach still need a person.
