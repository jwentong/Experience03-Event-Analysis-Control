"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""


def handle_timeout(c, e, s, actions):
    """仅处理当前有效且与呼叫阶段对应的定时器。"""
    if e.get("token") != c.timer or e.get("value") != c.timer_kind:
        return

    if c.timer_kind == "DIAL" and c.state == "COLLECTING":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE", reason="DIAL_TIMEOUT")
    elif c.timer_kind == "RING" and c.state == "RINGING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE", reason="NO_ANSWER")
