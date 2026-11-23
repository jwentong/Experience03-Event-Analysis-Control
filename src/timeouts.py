"""呼叫定时器超时处理。"""


def handle_timeout(c, e, s, actions):
    """先验证定时器代次和类型，再按呼叫状态处理有效超时。"""
    if e.get("token") != c.timer or e.get("value") != c.timer_kind:
        return

    timer_kind = e.get("value")
    if timer_kind == "DIAL" and c.state == "COLLECTING":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
    elif timer_kind == "RING" and c.state == "RINGING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")
