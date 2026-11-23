"""Hook transition detection for the event-driven exchange."""


def detect_hook_events(previous, current):
    """Return sorted OFFHOOK/ONHOOK transitions between two hook snapshots."""
    if set(previous) != set(current):
        raise ValueError("previous and current users must match")
    for snapshot in (previous, current):
        if any(value not in (0, 1) for value in snapshot.values()):
            raise ValueError("hook values must be 0 or 1")

    events = []
    for user in sorted(previous):
        before, after = previous[user], current[user]
        if before != after:
            events.append({"user": user, "kind": "OFFHOOK" if after else "ONHOOK"})
    return events
