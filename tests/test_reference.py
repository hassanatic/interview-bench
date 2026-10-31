from interview_bench.problems import get_problem, intervals as iv, request_logs as rl
import pytest


def test_request_log_references_on_the_sample():
    assert rl.ref_count_by_user(rl.SAMPLE) == {"alice": 3, "bob": 2, "carol": 1}
    assert rl.ref_top_users(rl.SAMPLE, 2) == ["alice", "bob"]
    assert rl.ref_rate_limited_users(rl.SAMPLE, 2, 10) == ["alice"]


def test_requests_exactly_one_window_apart_do_not_share_it():
    lines = ["0 amy GET / 200", "60 amy GET / 200"]
    assert rl.ref_rate_limited_users(lines, 1, 60) == []
    assert rl.ref_rate_limited_users(lines, 1, 61) == ["amy"]


def test_interval_references():
    assert iv.ref_merge([[1, 3], [8, 10], [2, 6], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert iv.ref_merge([[1, 3], [3, 5]]) == [[1, 5]]
    assert iv.ref_covered_length([[0, 5], [0, 5], [1, 2]]) == 5
    assert iv.ref_min_rooms([[0, 30], [30, 60]]) == 1
    assert iv.ref_min_rooms([[0, 10], [1, 11], [2, 12]]) == 3


def test_unknown_problem_names_the_options():
    with pytest.raises(KeyError, match="request-logs"):
        get_problem("nope")
