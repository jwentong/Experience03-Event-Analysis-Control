"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""


def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError('前后两次采样的用户集合必须一致')

    for user in previous:
        value = previous[user]
        if value not in (0, 1) or isinstance(value, bool):
            raise ValueError('挂机状态只能是0或1')
    for user in current:
        value = current[user]
        if value not in (0, 1) or isinstance(value, bool):
            raise ValueError('挂机状态只能是0或1')

    events = []
    for user in sorted(previous):
        before, after = previous[user], current[user]
        if before == after:
            continue
        events.append({'user': user, 'kind': 'OFFHOOK' if after == 1 else 'ONHOOK'})
    return events
