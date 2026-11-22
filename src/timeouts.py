"""Handle only timeout events that still match the active call timer."""


def handle_timeout(c, e, s, actions):
    """Ignore stale or mismatched timers; finish calls on valid timeouts."""
    if c.state == "ENDED" or e.get("token") != c.timer:
        return
    if e.get("value") != c.timer_kind:
        return

    if c.state == "COLLECTING" and c.timer_kind == "DIAL" and e.get("value") == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
    elif c.state == "RINGING" and c.timer_kind == "RING" and e.get("value") == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")
