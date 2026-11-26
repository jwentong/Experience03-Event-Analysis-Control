"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
def handle_timeout(c, e, s, actions):
    # 1. 状态校验：已接通/已结束的呼叫，旧定时器直接忽略
    if c.state in ("CONNECTED", "ENDED"):
        return
    # 2. token校验：事件token和当前呼叫定时器不匹配 → 旧定时器，忽略
    if e["token"] != c.timer:
        return
    # 3. 类型校验：超时类型和当前定时器类型不一致 → 忽略
    tk = e["value"]
    if tk != c.timer_kind:
        return

    # 只有有效超时才处理
    if tk == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        c.state = "ENDED"
        actions.append({"type": "FAIL_TONE", "user": c.caller})
    elif tk == "RING":
        s.finish(c, "NO_ANSWER")
        c.state = "ENDED"
        actions.append({"type": "STOP_RING", "user": c.callee})
        actions.append({"type": "FAIL_TONE", "user": c.caller})

