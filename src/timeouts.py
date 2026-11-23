"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if e.get("token") != c.timer:
        return
    if e.get("value") != c.timer_kind:
        return

    if c.state == "COLLECTING" and c.timer_kind == "DIAL" and e.get("value") == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE", user=c.caller)
        return

    if c.state == "RINGING" and c.timer_kind == "RING" and e.get("value") == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING", user=c.callee)
        s.action(actions, "FAIL_TONE", user=c.caller)
