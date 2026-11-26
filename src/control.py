"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c, e, s, actions):
    event_kind = e["kind"]
    caller = c.caller
    dial_plan = {"1001", "1002", "1003", "1004"}

    if event_kind == "OFFHOOK":
        if not c.callee:
            c.caller = e["user"]
            caller = c.caller
            c.state = "COLLECTING"
            c.digits = ""
            s.arm(c, "DIAL", 5000)
            actions.append({"type": "DIAL_TONE", "user": caller})

        if c.state == "RINGING" and e["user"] == c.callee:
            s.cancel(c)
            ok = s.activate(c)
            if ok:
                c.state = "CONNECTED"
                actions.append({"type": "STOP_RING", "user": c.callee})
                actions.append({"type": "CONNECT", "a": caller, "b": c.callee})
            else:
                s.finish(c, "NETWORK_BUSY")
                c.state = "ENDED"
                actions.append({"type": "FAIL_TONE", "user": caller})

    elif event_kind == "ONHOOK":
        if c.state != "ENDED":
            if c.state == "CONNECTED":
                s.finish(c, "NORMAL_CLEAR")
            else:
                s.finish(c, "CALLER_CANCEL")
            c.state = "ENDED"
            actions.append({"type": "RELEASE", "call_id": c.call_id})

    elif event_kind == "DIGIT":
        if c.state != "COLLECTING":
            return
        digit = e["value"]
        c.digits += digit
        res = analyze_number(c.digits, dial_plan, caller)
        actions.append({"type": "STOP_DIAL_TONE", "user": caller})

        if res == "INCOMPLETE":
            actions.append({"type": "DIAL_TONE", "user": caller})
        elif res == "SELF_CALL":
            s.finish(c, "SELF_CALL")
            c.state = "ENDED"
            actions.append({"type": "FAIL_TONE", "user": caller})
        elif res == "INVALID":
            s.finish(c, "INVALID")
            c.state = "ENDED"
            actions.append({"type": "FAIL_TONE", "user": caller})
        elif res == "LOCAL":
            called = c.digits
            s.cancel(c)
            reserved_ok = s.reserve(c, called)
            if not reserved_ok:
                s.finish(c, "USER_BUSY")
                c.state = "ENDED"
                actions.append({"type": "BUSY_TONE", "user": caller})
            else:
                c.state = "RINGING"
                c.callee = called
                s.arm(c, "RING", 10000)
                actions.append({"type": "RING", "user": called})
                actions.append({"type": "RINGBACK", "user": caller})
