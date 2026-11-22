"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous) != set(current):
        raise ValueError("用户集合不一致")
    if any(value not in (0, 1) for sample in (previous, current)
           for value in sample.values()):
        raise ValueError("摘挂机采样必须为0或1")
    return [
        {'user': user, 'kind': 'OFFHOOK' if current[user] else 'ONHOOK'}
        for user in sorted(previous) if previous[user] != current[user]
    ]
