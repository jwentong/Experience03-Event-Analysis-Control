"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if previous.keys() != current.keys():
        raise ValueError("前后采样的用户集合必须一致")

    events = []
    for user in sorted(current):
        before, after = previous[user], current[user]
        if before not in (0, 1) or after not in (0, 1):
            raise ValueError("摘挂机采样值必须为0或1")
        if before != after:
            kind = "OFFHOOK" if after == 1 else "ONHOOK"
            events.append({"user": user, "kind": kind})
    return events
