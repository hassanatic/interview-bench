# Correct answers, but part 3 compares every request with every other request.
from logs_good import count_by_user, top_users  # noqa: F401


def rate_limited_users(lines, limit, window):
    stamps = {}
    for line in lines:
        ts, user = line.split()[:2]
        stamps.setdefault(user, []).append(int(ts))
    flagged = set()
    for user, times in stamps.items():
        for t in times:
            inside = sum(1 for other in times if t - window < other <= t)
            if inside > limit:
                flagged.add(user)
                break
    return sorted(flagged)
