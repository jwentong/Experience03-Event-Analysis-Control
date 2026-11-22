"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    if set(previous)!=set(current):
        raise ValueError('两次采样的用户集合不一致')
    events=[]
    for user in sorted(previous):
        p=previous[user];c=current[user]
        if p not in (0,1) or c not in (0,1):
            raise ValueError('采样值只能是0（挂机）或1（摘机）')
        if p==0 and c==1:
            events.append({'user':user,'kind':'OFFHOOK'})
        elif p==1 and c==0:
            events.append({'user':user,'kind':'ONHOOK'})
    return events
