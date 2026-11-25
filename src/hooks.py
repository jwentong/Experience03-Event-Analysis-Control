"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError('前后两次采样的用户集合必须一致')
    events = []
    for user in sorted(previous):
        before, after = previous[user], current[user]
        if before not in (0, 1) or after not in (0, 1):
            raise ValueError('摘挂机采样只能是0（挂机）或1（摘机）')
        if before == 0 and after == 1:
            events.append({'user': user, 'kind': 'OFFHOOK'})
        elif before == 1 and after == 0:
            events.append({'user': user, 'kind': 'ONHOOK'})
    return events
