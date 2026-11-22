"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

_VALID_HOOK_VALUES=(0,1)

def detect_hook_events(previous,current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    # 前后采样必须覆盖同一批用户，否则无法逐用户比较
    if set(previous)!=set(current):
        raise ValueError("摘挂机采样的用户集合不一致")
    events=[]
    for user in sorted(previous):
        before,after=previous[user],current[user]
        # 先校验采样值，再比较跳变：即使该用户采样没变化，非法值也要报错
        if before not in _VALID_HOOK_VALUES or after not in _VALID_HOOK_VALUES:
            raise ValueError(f"用户 {user} 的摘挂机采样值非法：{before!r} -> {after!r}")
        if before==after:
            continue  # 重复采样不产生事件
        events.append({'user':user,'kind':'OFFHOOK' if after==1 else 'ONHOOK'})
    return events
