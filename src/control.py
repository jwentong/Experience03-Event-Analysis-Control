"""呼叫事件控制逻辑。"""
from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """按呼叫状态处理事件，并通过Exchange服务管理定时器及话路。"""
    kind = e.get("kind")

    if kind == "OFFHOOK":
        if c.state == "COLLECTING" and e.get("user") == c.caller:
            s.action(actions, "DIAL_TONE")
            s.arm(c, "DIAL", 5000)
            return

        if c.state == "RINGING" and e.get("user") == c.callee:
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

    if kind == "DIGIT" and c.state == "COLLECTING":
        if e.get("user") != c.caller:
            return

        c.digits += str(e.get("value", ""))
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

    if kind == "ONHOOK" and c.state in ("COLLECTING", "RINGING", "CONNECTED"):
        if e.get("user") not in (c.caller, c.callee):
            return

        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE")
