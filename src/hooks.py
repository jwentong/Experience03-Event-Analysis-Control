"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""


def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError('hook samples must be dictionaries')
    if set(previous) != set(current):
        raise ValueError('hook samples must contain the same users')

    events = []
    for user in sorted(previous):
        before = previous[user]
        after = current[user]
        if isinstance(before, bool) or before not in (0, 1):
            raise ValueError('hook values must be 0 or 1')
        if isinstance(after, bool) or after not in (0, 1):
            raise ValueError('hook values must be 0 or 1')
        if before == after:
            continue
        events.append({'user': user, 'kind': 'OFFHOOK' if after == 1 else 'ONHOOK'})
    return events
