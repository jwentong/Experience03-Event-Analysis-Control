"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c, e, s, actions):
    # 已结束的呼叫：旧定时器直接忽略，不改状态、话路和资源
    if c.state == "ENDED":
        return

    # 先校验 token 与 timer_kind，旧定时器或不匹配类型直接忽略
    if e["token"] != c.timer or e["value"] != c.timer_kind:
        return

    # 有效 DIAL 超时
    if c.state == "COLLECTING" and e["value"] == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
        c.state = "ENDED"
        return

    # 有效 RING 超时
    if c.state == "RINGING" and e["value"] == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")
        c.state = "ENDED"
        return