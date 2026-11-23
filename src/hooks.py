"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    # 1. 校验用户集合是否完全一致
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("用户集合不一致")

    users = list(previous.keys())
    # 2. 校验所有采样值只能是0或1
    for u in users:
        prev_val = previous[u]
        curr_val = current[u]
        if prev_val not in (0, 1) or curr_val not in (0, 1):
            raise ValueError("采样值非法，只能为0或1")

    event_list = []
    # 3. 遍历每个用户，判断状态跃迁
    for user in sorted(users):  # 按用户编号排序
        p = previous[user]
        c = current[user]
        if p == c:
            # 状态不变，不生成事件
            continue
        if p == 0 and c == 1:
            # 挂机 → 摘机
            event_list.append({"user": user, "kind": "OFFHOOK"})
        elif p == 1 and c == 0:
            # 摘机 → 挂机
            event_list.append({"user": user, "kind": "ONHOOK"})
    return event_list
