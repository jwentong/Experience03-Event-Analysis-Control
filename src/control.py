"""Control collection, ringing, answer and release of a subscriber call."""

from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """Process a subscriber event using the exchange's resource services."""
    if c.state == "ENDED":
        return

    kind, user = e["kind"], e.get("user")
    if user is None or user not in (c.caller, c.callee):
        return

    if kind == "ONHOOK":
        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE", user=user, reason=reason)
    elif kind == "OFFHOOK":
        if c.state == "COLLECTING" and user == c.caller and c.timer_kind is None:
            s.action(actions, "DIAL_TONE", user=c.caller)
            s.arm(c, "DIAL", 5000)
        elif c.state == "RINGING" and user == c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING", user=c.callee)
                s.action(actions, "CONNECT", caller=c.caller, callee=c.callee)
            else:
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE", user=c.caller, reason=c.reason)
    elif kind == "DIGIT" and c.state == "COLLECTING" and user == c.caller:
        c.digits += e["value"]
        result = analyze_number(c.digits, s.numbers, c.caller)
        if result == "INCOMPLETE":
            s.action(actions, "STOP_DIAL_TONE", user=c.caller)
        elif result in ("INVALID", "SELF_CALL"):
            s.finish(c, result)
            s.action(actions, "FAIL_TONE", user=c.caller, reason=result)
        elif not s.reserve(c, c.digits):
            s.finish(c, "USER_BUSY")
            s.action(actions, "BUSY_TONE", user=c.caller, reason=c.reason)
        else:
            s.cancel(c)
            c.state = "RINGING"
            s.arm(c, "RING", 10000)
            s.action(actions, "RING", user=c.callee)
            s.action(actions, "RINGBACK", user=c.caller)
