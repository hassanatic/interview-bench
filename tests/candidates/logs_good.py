from collections import defaultdict


def count_by_user(lines):
    counts = {}
    for line in lines:
        user = line.split()[1]
        counts[user] = counts.get(user, 0) + 1
    return counts


def top_users(lines, k):
    counts = count_by_user(lines)
    return sorted(counts, key=lambda u: (-counts[u], u))[:k]


def rate_limited_users(lines, limit, window):
    times = defaultdict(list)
    for line in lines:
        ts, user = line.split()[:2]
        times[user].append(int(ts))
    flagged = []
    for user, stamps in times.items():
        stamps.sort()
        left = 0
        for right, ts in enumerate(stamps):
            while stamps[left] <= ts - window:
                left += 1
            if right - left + 1 > limit:
                flagged.append(user)
                break
    return sorted(flagged)
