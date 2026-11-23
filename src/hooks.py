"""摘机、挂机采样去重。"""


def detect_hook_events(previous, current):
    """比较两次用户状态采样，按用户编号排序返回边沿事件。"""
    if set(previous) != set(current):
        raise ValueError("用户集合不一致")

    for value in (*previous.values(), *current.values()):
        if isinstance(value, bool) or not isinstance(value, int) or value not in (0, 1):
            raise ValueError("用户状态只能为0或1")

    events = []
    for user in sorted(current):
        old, new = previous[user], current[user]
        if old == new:
            continue
        events.append({"user": user, "kind": "OFFHOOK" if new == 1 else "ONHOOK"})
    return events
