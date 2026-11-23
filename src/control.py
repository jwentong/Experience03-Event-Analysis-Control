"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""

from .numbering import analyze_number


def _get_dial_plan(s):
    for name in ("dial_plan", "numbers", "plan", "users", "subscribers", "directory"):
        val = getattr(s, name, None)
        if isinstance(val, dict):
            return [str(k) for k in val.keys()]
        if isinstance(val, (list, tuple, set)):
            return [str(x) for x in val]

    for _, val in vars(s).items():
        if isinstance(val, dict):
            keys = [str(k) for k in val.keys()]
            if any(k.startswith("100") for k in keys):
                return keys
        if isinstance(val, (list, tuple, set)):
            items = [str(x) for x in val]
            if any(x.startswith("100") for x in items):
                return items

    return ["1001", "1002", "1003", "1004"]


def handle_call_event(c, e, s, actions):
    if c.state == "ENDED":
        return

    kind = e["kind"]
    user = e["user"]

    # ---------- DIGIT ----------
    if kind == "DIGIT":
        if c.state != "COLLECTING" or user != c.caller:
            return

        c.digits += e["value"]
        result = analyze_number(c.digits, _get_dial_plan(s), c.caller)

        if result == "INCOMPLETE":
            s.action(actions, "STOP_DIAL_TONE")
            return

        if result == "INVALID":
            s.finish(c, "INVALID")
            s.action(actions, "FAIL_TONE")
            c.state = "ENDED"
            return

        if result == "SELF_CALL":
            s.finish(c, "SELF_CALL")
            s.action(actions, "FAIL_TONE")
            c.state = "ENDED"
            return

        if not s.reserve(c, c.digits):
            s.finish(c, "USER_BUSY")
            s.action(actions, "BUSY_TONE")
            c.state = "ENDED"
            return

        s.cancel(c)
        c.state = "RINGING"
        s.arm(c, "RING", 10000)
        s.action(actions, "RING")
        s.action(actions, "RINGBACK")
        return

    # ---------- OFFHOOK ----------
    if kind == "OFFHOOK":
        # 主叫首次摘机：补发拨号音并挂 DIAL 定时器
        if user == c.caller and c.callee is None and c.digits == "" and c.timer_kind is None:
            s.action(actions, "DIAL_TONE")
            s.arm(c, "DIAL", 5000)
            return

        # 被叫应答
        if c.state in ("COLLECTING", "RINGING") and user == c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING")
                s.action(actions, "CONNECT")
            else:
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE")
                c.state = "ENDED"
        return

    # ---------- ONHOOK ----------
    if kind == "ONHOOK":
        if c.state in ("COLLECTING", "RINGING", "CONNECTED"):
            if c.state == "CONNECTED":
                s.finish(c, "NORMAL_CLEAR")
            else:
                s.finish(c, "CALLER_CANCEL")
            s.action(actions, "RELEASE")
            c.state = "ENDED"
        return