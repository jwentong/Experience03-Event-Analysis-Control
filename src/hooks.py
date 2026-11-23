"""Detect changes between two samples of subscriber hook states."""


def detect_hook_events(previous, current):
    """Return changes ordered by subscriber number after validating samples."""
    if previous.keys() != current.keys():
        raise ValueError("两次采样的用户集合不一致")

    events = []
    for user in sorted(previous):
        old, new = previous[user], current[user]
        if old not in (0, 1) or new not in (0, 1):
            raise ValueError(f"用户 {user} 的采样值必须为 0 或 1")
        if old != new:
            kind = "OFFHOOK" if new == 1 else "ONHOOK"
            events.append({"user": user, "kind": kind})
    return events
