"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous, current):
    """按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""
    
    # 1. 检查用户集合是否一致
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("前后采样的用户集合不一致")
        
    events = []
    
    # 2. 按用户编号排序遍历，保证输出的顺序是一致的
    for user in sorted(previous.keys()):
        prev_state = previous[user]
        curr_state = current[user]
        
        # 检查值是否合法（只能是 0 或 1）
        if prev_state not in (0, 1) or curr_state not in (0, 1):
            raise ValueError(f"用户 {user} 的状态值非法，只能是 0 或 1")
            
        # 3. 判断状态变化
        if prev_state == 0 and curr_state == 1:
            events.append({"user": user, "kind": "OFFHOOK"})
        elif prev_state == 1 and curr_state == 0:
            events.append({"user": user, "kind": "ONHOOK"})
            
    return events