"""将用户摘挂机采样变化转换为有序事件。"""


def detect_hook_events(previous, current):
    """Return sorted hook events, rejecting inconsistent users or samples."""
    if previous.keys() != current.keys():
        raise ValueError("用户集合不一致")

    events = []
    for user in sorted(previous):
        old_value = previous[user]
        new_value = current[user]
        if old_value not in (0, 1) or new_value not in (0, 1):
            raise ValueError("摘挂机采样值必须为0或1")
        if old_value != new_value:
            events.append({
                "user": user,
                "kind": "OFFHOOK" if new_value == 1 else "ONHOOK",
            })
    return events
