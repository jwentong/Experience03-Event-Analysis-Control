"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if e.get("kind") != "TIMEOUT" or e.get("token") != c.timer:
        return

    timer_kind = e.get("value")
    if timer_kind != c.timer_kind:
        return

    if c.state == "COLLECTING" and timer_kind == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE", reason="DIAL_TIMEOUT")
    elif c.state == "RINGING" and timer_kind == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE", reason="NO_ANSWER")
