"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """根据事件更新呼叫状态，通过交换机服务管理资源。"""
    if c.state == "ENDED":
        return

    kind, user = e["kind"], e.get("user")
    if kind == "ONHOOK":
        if user is None or user not in (c.caller, c.callee):
            return
        reason = "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL"
        s.finish(c, reason)
        s.action(actions, "RELEASE")
        return

    if kind == "OFFHOOK":
        if c.state == "COLLECTING" and user == c.caller and c.timer_kind is None:
            s.action(actions, "DIAL_TONE")
            s.arm(c, "DIAL", 5000)
        elif c.state == "RINGING" and user == c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING")
                s.action(actions, "CONNECT")
            else:
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE", reason="NETWORK_BUSY")
        return

    if kind != "DIGIT" or user != c.caller or c.state != "COLLECTING":
        return

    c.digits += e["value"]
    s.action(actions, "STOP_DIAL_TONE")
    result = analyze_number(c.digits, s.numbers, c.caller)
    if result == "INCOMPLETE":
        return
    if result in ("INVALID", "SELF_CALL"):
        s.finish(c, result)
        s.action(actions, "FAIL_TONE", reason=result)
        return
    if not s.reserve(c, c.digits):
        s.finish(c, "USER_BUSY")
        s.action(actions, "BUSY_TONE")
        return

    s.cancel(c)
    c.state = "RINGING"
    s.arm(c, "RING", 10000)
    s.action(actions, "RING", user=c.callee)
    s.action(actions, "RINGBACK", user=c.caller)
