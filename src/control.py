"""呼叫控制：按状态表原地修改 Call，并通过框架服务操作真实话路。"""
from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    kind = e["kind"]

    if kind == "OFFHOOK":
        # 新呼叫：框架刚创建 Call，还没有任何定时器
        if c.state == "COLLECTING" and c.timer == 0:
            s.action(actions, "DIAL_TONE")
            s.arm(c, "DIAL", 5000)
            return

        # 被叫应答：只有被叫的摘机才是应答，主叫本来就处于摘机状态
        if c.state == "RINGING" and e.get("user") == c.callee:
            s.cancel(c)  # 先作废振铃超时，避免 10400ms 的旧事件拆掉已接通呼叫
            if s.activate(c):  # 建立双向 T/S 映射
                c.state = "CONNECTED"
                s.action(actions, "STOP_RING")
                s.action(actions, "CONNECT")
            else:  # 网络侧拒绝
                s.finish(c, "NETWORK_BUSY")
                s.action(actions, "FAIL_TONE")
        return

    if kind == "DIGIT":
        # 只接受主叫在收号状态输入的数字
        if c.state != "COLLECTING" or e.get("user") != c.caller:
            return

        c.digits += str(e["value"])
        verdict = analyze_number(c.digits, s.numbers, c.caller)

        if verdict == "INCOMPLETE":
            s.action(actions, "STOP_DIAL_TONE")
            return

        if verdict == "SELF_CALL":
            s.finish(c, "SELF_CALL")
            s.action(actions, "FAIL_TONE")
            return

        if verdict == "INVALID":
            s.finish(c, "INVALID")
            s.action(actions, "FAIL_TONE")
            return

        # verdict == "LOCAL"：先抢被叫资源，抢到才振铃
        if not s.reserve(c, c.digits):
            s.finish(c, "USER_BUSY")
            s.action(actions, "BUSY_TONE")
            return

        s.cancel(c)  # 作废收号总超时
        c.state = "RINGING"
        s.arm(c, "RING", 10000)
        s.action(actions, "RING")
        s.action(actions, "RINGBACK")
        return

    if kind == "ONHOOK":
        if c.state == "ENDED":
            return
        # 通话中挂机是正常拆线，通话前挂机是主叫放弃
        s.finish(c, "NORMAL_CLEAR" if c.state == "CONNECTED" else "CALLER_CANCEL")
        s.action(actions, "RELEASE")
