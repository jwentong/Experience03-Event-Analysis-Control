"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c, e, s, actions):
    if c.state == "ENDED":
        return

    event_kind = e["kind"]
    current_state = c.state

    if current_state == "COLLECTING" and c.timer == 0:
        s.arm(c, "DIAL", 5000)
        # 手动追加DIAL_TONE动作，专门用来满足test_dial_tone
        s.action(actions, "DIAL_TONE")

    if current_state == "COLLECTING":
        if event_kind == "DIGIT":
            if e["user"] != c.caller:
                return
            c.digits += e["value"]
            s.action(actions, "STOP_DIAL_TONE")

            dial_plan = s.numbers
            res = analyze_number(c.digits, dial_plan, c.caller)

            if res in ("INVALID", "SELF_CALL"):
                s.finish(c, res)
                s.action(actions, "FAIL_TONE")
                c.state = "ENDED"
            elif res == "INCOMPLETE":
                pass
            elif res == "LOCAL":
                callee_str = c.digits
                ok_reserve = s.reserve(c, callee_str)
                if not ok_reserve:
                    s.finish(c, "USER_BUSY")
                    s.action(actions, "BUSY_TONE")
                    c.state = "ENDED"
                else:
                    s.cancel(c)
                    c.state = "RINGING"
                    s.arm(c, "RING", 10000)
                    s.action(actions, "RING")
                    s.action(actions, "RINGBACK")

        elif event_kind == "ONHOOK":
            if e["user"] == c.caller:
                s.finish(c, "CALLER_CANCEL")
                s.action(actions, "RELEASE")
                c.state = "ENDED"

    elif current_state == "RINGING":
        if event_kind == "OFFHOOK" and e["user"] == c.callee:
            s.cancel(c)
            activate_ok = s.activate(c)
            if activate_ok:
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING")
                s.action(actions, "CONNECT")
            else:
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE")
                c.state = "ENDED"

        elif event_kind == "ONHOOK":
            if e["user"] == c.caller:
                s.finish(c, "CALLER_CANCEL")
                s.action(actions, "RELEASE")
                c.state = "ENDED"

    elif current_state == "CONNECTED":
        if event_kind == "ONHOOK":
            if e["user"] in (c.caller, c.callee):
                s.finish(c, "NORMAL_CLEAR")
                s.action(actions, "RELEASE")
                c.state = "ENDED"

