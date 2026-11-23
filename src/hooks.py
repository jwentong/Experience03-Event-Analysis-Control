"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError("用户集合不一致")
    events = []
    for user in previous:
        pv = previous[user]
        cv = current[user]
        if pv not in (0, 1) or cv not in (0, 1):
            raise ValueError("非法采样值")
        if pv == cv:
            continue
        kind = 'OFFHOOK' if pv == 0 and cv == 1 else 'ONHOOK'
        events.append({'user': user, 'kind': kind})
    events.sort(key=lambda x: x['user'])
    return events
