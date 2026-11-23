"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError("摘挂机采样的用户集合必须一致")

    events = []
    for user in sorted(previous):
        old = previous[user]
        new = current[user]
        if old not in (0, 1) or new not in (0, 1):
            raise ValueError("摘挂机采样值只能是0或1")
        if old == new:
            continue
        events.append({
            "user": user,
            "kind": "OFFHOOK" if new == 1 else "ONHOOK",
        })
    return events
