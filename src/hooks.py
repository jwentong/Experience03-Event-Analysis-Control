"""摘挂机事件检测。"""


def detect_hook_events(previous, current):
    """根据相邻两次采样生成摘挂机事件列表。"""

    # 两次采样必须包含完全相同的用户
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("前后采样的用户集合不一致")

    # 采样值只能是整数0或1
    for samples in (previous, current):
        for value in samples.values():
            if type(value) is not int or value not in (0, 1):
                raise ValueError("摘挂机采样值只能是0或1")

    events = []

    # 按用户编号排序，确保事件顺序固定
    for user in sorted(previous.keys()):
        old_value = previous[user]
        new_value = current[user]

        if old_value == 0 and new_value == 1:
            events.append({
                "user": user,
                "kind": "OFFHOOK",
            })
        elif old_value == 1 and new_value == 0:
            events.append({
                "user": user,
                "kind": "ONHOOK",
            })

    return events