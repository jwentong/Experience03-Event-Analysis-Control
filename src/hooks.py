"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous)!=set(current):raise ValueError('用户集合不一致')
    if any(v not in (0,1) for v in previous.values()) or any(v not in (0,1) for v in current.values()):raise ValueError('采样值必须为0或1')
    events=[]
    for user in sorted(previous):
        if previous[user]==current[user]:continue
        events.append({'user':user,'kind':'OFFHOOK' if current[user]==1 else 'ONHOOK'})
    return events
