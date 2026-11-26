"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
"""按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous, current):

    # 1. 用户集合校验
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("user set mismatch")

    events = []
    # 遍历，先校验取值，再判断跳变
    for user in previous:
        pv = previous[user]
        cv = current[user]
        if pv not in (0, 1) or cv not in (0, 1):
            raise ValueError("hook value must be 0 or 1")

        if pv == 0 and cv == 1:
            events.append({"user": user, "kind": "OFFHOOK"})
        elif pv == 1 and cv == 0:
            events.append({"user": user, "kind": "ONHOOK"})
        # pv == cv：无事件，跳过

    # 2. 按用户编号升序排序
    events.sort(key=lambda x: x["user"])
    return events



