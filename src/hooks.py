"""摘挂机检测：把相邻两次采样之间的电平跳变翻译成 OFFHOOK / ONHOOK 事件。"""


def detect_hook_events(previous, current):
    # 两次采样必须覆盖同一批用户，否则调用方传错了数据
    if set(previous) != set(current):
        raise ValueError("前后两次采样必须覆盖同一批用户")

    events = []
    # 按用户编号排序，保证同一时刻多个边沿的输出顺序稳定
    for user in sorted(current):
        before = previous[user]
        after = current[user]
        # 采样只允许 0（挂机）和 1（摘机）
        if before not in (0, 1) or after not in (0, 1):
            raise ValueError(f"用户 {user} 的采样值必须是 0 或 1")
        # 电平没变就没有事件
        if before == after:
            continue
        events.append({"user": user, "kind": "OFFHOOK" if after == 1 else "ONHOOK"})
    return events
