"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("user sets differ")

    events = []
    for user in sorted(current.keys()):
        prev = previous[user]
        cur = current[user]
        if prev not in (0, 1) or cur not in (0, 1):
            raise ValueError("invalid hook value")
        if prev == cur:
            continue
        kind = "OFFHOOK" if cur == 1 else "ONHOOK"
        events.append({"kind": kind, "user": user})
    return events
