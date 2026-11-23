"""学生任务：按用户编号排序返回{user,kind}列表；0→1为OFFHOOK，1→0为ONHOOK，相同不产生事件。集合不一致或值非0/1抛ValueError。"""

def detect_hook_events(previous: dict, current: dict) -> list[dict]:
    if set(previous.keys()) != set(current.keys()):
        raise ValueError("previous 与 current 的用户集合不一致")

    events = []
    for user in sorted(current.keys()):
        prev_val = previous[user]
        curr_val = current[user]

        if prev_val not in (0, 1) or curr_val not in (0, 1):
            raise ValueError(f"用户 {user} 的采样值非法: {prev_val}, {curr_val}")

        if prev_val == curr_val:
            continue

        kind = "OFFHOOK" if curr_val == 1 else "ONHOOK"
        events.append({"kind": kind, "user": user})

    return events
