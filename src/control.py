"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == "ENDED":
        return

    kind = e.get("kind")
    user = e.get("user")

    if kind == "DIGIT":
        if c.state != "COLLECTING" or user != c.caller:
            return
        c.digits = (c.digits or "") + e.get("value", "")
        result = analyze_number(c.digits, s.numbers, c.caller)

        if result == "INCOMPLETE":
            s.action(actions, "STOP_DIAL_TONE")
        elif result == "LOCAL":
            if s.reserve(c, c.digits):
                s.cancel(c)
                c.state = "RINGING"
                s.arm(c, "RING", 10000)
                s.action(actions, "RING")
                s.action(actions, "RINGBACK")
            else:
                s.finish(c, "USER_BUSY")
                s.action(actions, "BUSY_TONE")
        else:
            s.finish(c, result)
            s.action(actions, "FAIL_TONE")
        return

    if kind == "OFFHOOK":
        if c.state == "COLLECTING" and user == c.caller:
            s.action(actions, "DIAL_TONE")
            s.arm(c, "DIAL", 5000)
            return
        if c.state == "RINGING" and user == c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING")
                s.action(actions, "CONNECT")
            else:
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE")
        return

    if kind == "ONHOOK":
        if c.state in ("COLLECTING", "RINGING"):
            if user == c.caller:
                s.finish(c, "CALLER_CANCEL")
                s.action(actions, "RELEASE")
        elif c.state == "CONNECTED":
            if user in (c.caller, c.callee):
                s.finish(c, "NORMAL_CLEAR")
                s.action(actions, "RELEASE")
        return
