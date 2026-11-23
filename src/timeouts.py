"""Handle only the current timer of an active call."""


def handle_timeout(c, e, s, actions):
    """Require the token, timer type and call state to match."""
    kind = e.get("value")
    if e.get("token") != c.timer or kind != c.timer_kind:
        return

    if kind == "DIAL" and c.state == "COLLECTING":
        reason = "DIAL_TIMEOUT"
    elif kind == "RING" and c.state == "RINGING":
        reason = "NO_ANSWER"
        s.action(actions, "STOP_RING", user=c.callee)
    else:
        return

    s.finish(c, reason)
    s.action(actions, "FAIL_TONE", user=c.caller, reason=reason)
