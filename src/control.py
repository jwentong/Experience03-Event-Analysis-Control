"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == "ENDED":
        return

    kind, user = e["kind"], e["user"]
    if kind == "ONHOOK" and user is not None and user in (c.caller, c.callee):
        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE")
        return

    if c.state == "RINGING" and kind == "OFFHOOK" and user == c.callee:
        s.cancel(c)
        if s.activate(c):
            c.state = "CONNECTED"
            s.action(actions, "STOP_RING")
            s.action(actions, "CONNECT")
        else:
            s.finish(c, "NETWORK_BUSY")
            s.action(actions, "FAIL_TONE")
        return

    if c.state != "COLLECTING" or user != c.caller:
        return
    if kind == "OFFHOOK" and c.timer_kind is None:
        s.action(actions, "DIAL_TONE")
        s.arm(c, "DIAL", 5000)
    if kind != "DIGIT":
        return

    digit = e["value"]
    if isinstance(digit, str) and len(digit) == 1:
        c.digits += digit
        result = analyze_number(c.digits, s.numbers, c.caller)
    else:
        result = "INVALID"

    if result == "INCOMPLETE":
        s.action(actions, "STOP_DIAL_TONE")
    elif result in ("INVALID", "SELF_CALL"):
        s.finish(c, result)
        s.action(actions, "FAIL_TONE")
    elif not s.reserve(c, c.digits):
        s.finish(c, "USER_BUSY")
        s.action(actions, "BUSY_TONE")
    else:
        s.cancel(c)
        c.state = "RINGING"
        s.arm(c, "RING", 10000)
        s.action(actions, "RING")
        s.action(actions, "RINGBACK")
