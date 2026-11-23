"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == "ENDED":
        return

    kind = e.get("kind")

    if c.state == "COLLECTING":
        if kind == "OFFHOOK" and e.get("user") == c.caller and c.timer_kind is None:
            s.action(actions, "DIAL_TONE", user=c.caller)
            s.arm(c, "DIAL", 5000)
            return

        if kind == "DIGIT" and e.get("user") == c.caller:
            value = e.get("value")
            c.digits += "" if not isinstance(value, str) else value
            result = analyze_number(c.digits, s.numbers, c.caller)

            if result == "INCOMPLETE":
                s.action(actions, "STOP_DIAL_TONE", user=c.caller)
                return

            if result == "INVALID":
                s.finish(c, "INVALID")
                s.action(actions, "FAIL_TONE", user=c.caller)
                return

            if result == "SELF_CALL":
                s.finish(c, "SELF_CALL")
                s.action(actions, "FAIL_TONE", user=c.caller)
                return

            if not s.reserve(c, c.digits):
                s.finish(c, "USER_BUSY")
                s.action(actions, "BUSY_TONE", user=c.caller)
                return

            s.cancel(c)
            c.state = "RINGING"
            s.arm(c, "RING", 10000)
            s.action(actions, "RING", user=c.callee)
            s.action(actions, "RINGBACK", user=c.caller)

        return

    if kind == "ONHOOK":
        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE", caller=c.caller, callee=c.callee)
        return

    if c.state == "RINGING" and kind == "OFFHOOK" and e.get("user") == c.callee:
        s.cancel(c)
        if s.activate(c):
            c.state = "CONNECTED"
            s.action(actions, "STOP_RING", user=c.callee)
            s.action(actions, "CONNECT", caller=c.caller, callee=c.callee)
        else:
            s.finish(c, "NETWORK_BUSY")
            s.action(actions, "FAIL_TONE", user=c.caller)
