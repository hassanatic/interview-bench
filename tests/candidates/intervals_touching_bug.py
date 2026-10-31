# Treats touching intervals as separate and back-to-back meetings as overlapping.


def merge(intervals):
    out = []
    for start, end in sorted(intervals):
        if out and start < out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out


def covered_length(intervals):
    return sum(end - start for start, end in merge(intervals))


def min_rooms(meetings):
    events = sorted([(s, 0) for s, _ in meetings] + [(e, 1) for _, e in meetings])
    rooms = best = 0
    for _, kind in events:
        rooms += 1 if kind == 0 else -1
        best = max(best, rooms)
    return best
