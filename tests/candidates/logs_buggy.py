# Part 1 is right; part 2 forgets the tie-break; part 3 was never written.


def count_by_user(lines):
    counts = {}
    for line in lines:
        user = line.split()[1]
        counts[user] = counts.get(user, 0) + 1
    return counts


def top_users(lines, k):
    counts = count_by_user(lines)
    return sorted(counts, key=lambda u: -counts[u])[:k]
