"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def _check_sample(sample,name):
    """检查一份采样：必须是字典，且每个值只能是0（挂机）或1（摘机）。"""
    if not isinstance(sample,dict):
        raise ValueError(f'{name}必须是号码到0/1的字典')
    for user,value in sample.items():
        if value not in (0,1):
            raise ValueError(f'{name}中{user}的采样值{value!r}非法')

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    _check_sample(previous,'previous')
    _check_sample(current,'current')
    if set(previous)!=set(current):
        raise ValueError('前后采样的用户集合必须一致')
    events=[]
    # 排序保证同一时刻的多个用户事件顺序确定，日志可逐条核对；入参只读不改。
    for user in sorted(current):
        before=previous[user]
        after=current[user]
        if before==after:
            continue
        events.append({'user':user,'kind':'OFFHOOK' if after==1 else 'ONHOOK'})
    return events
