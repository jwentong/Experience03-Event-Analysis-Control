"""Call-event state transitions for the event-driven exchange."""
from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """Update a call in place and record its corresponding exchange actions."""
    if c.state == "ENDED":
        return

    kind = e.get("kind")
    user = e.get("user")

    if kind == "OFFHOOK" and user == c.caller and c.state == "COLLECTING":
        s.action(actions, "DIAL_TONE")
        s.arm(c, "DIAL", 5000)
        return

    if kind == "DIGIT" and user == c.caller and c.state == "COLLECTING":
        value = e.get("value")
        if not isinstance(value, str) or len(value) != 1:
            return

        c.digits += value
        result = analyze_number(c.digits, s.numbers, c.caller)
        s.action(actions, "STOP_DIAL_TONE")
        if result == "INCOMPLETE":
            return
        if result in ("INVALID", "SELF_CALL"):
            s.finish(c, result)
            s.action(actions, "FAIL_TONE")
            return
        if not s.reserve(c, c.digits):
            s.finish(c, "USER_BUSY")
            s.action(actions, "BUSY_TONE")
            return

        s.cancel(c)
        c.state = "RINGING"
        s.arm(c, "RING", 10000)
        s.action(actions, "RING")
        s.action(actions, "RINGBACK")
        return

    if kind == "OFFHOOK" and user == c.callee and c.state == "RINGING":
        s.cancel(c)
        if s.activate(c):
            c.state = "CONNECTED"
            s.action(actions, "STOP_RING")
            s.action(actions, "CONNECT")
        else:
            s.finish(c, "NETWORK_BUSY")
            s.action(actions, "STOP_RING")
            s.action(actions, "FAIL_TONE")
        return

    if kind == "ONHOOK" and user in (c.caller, c.callee):
        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE")
