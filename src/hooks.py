"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError("采样中的用户集合必须一致")
    if any(type(value) is not int or value not in (0, 1) for value in (*previous.values(), *current.values())):
        raise ValueError("摘挂机采样值只能为0或1")

    events = []
    for user in sorted(previous):
        if previous[user] != current[user]:
            kind = "OFFHOOK" if current[user] == 1 else "ONHOOK"
            events.append({"user": user, "kind": kind})
    return events
