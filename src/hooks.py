"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError('前后两次采样的用户集合不一致')
    for value in list(previous.values()) + list(current.values()):
        if value not in (0, 1):
            raise ValueError('采样值只能是0（挂机）或1（摘机）')
    events = []
    for user in sorted(previous):
        before = previous[user]
        after = current[user]
        if before == after:
            continue
        events.append({'user': user, 'kind': 'OFFHOOK' if after == 1 else 'ONHOOK'})
    return events
