"""呼叫事件控制。"""

from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """根据呼叫状态和输入事件更新呼叫，并调用交换机服务。"""

    # 已结束的呼叫不再处理其他事件
    if c.state == "ENDED":
        return

    kind = e.get("kind")
    user = e.get("user")

    # 1. 被叫在振铃状态下摘机应答
    if (
        c.state == "RINGING"
        and kind == "OFFHOOK"
        and user == c.callee
    ):
        s.cancel(c)

        if s.activate(c):
            c.state = "CONNECTED"
            s.action(actions, "STOP_RING", user=c.callee)
            s.action(
                actions,
                "CONNECT",
                caller=c.caller,
                callee=c.callee,
            )
        else:
            s.finish(c, "NETWORK_BUSY")
            s.action(actions, "FAIL_TONE", user=c.caller)

        return

    # 2. 主叫首次摘机，播放拨号音并启动收号总定时器
    if (
        c.state == "COLLECTING"
        and kind == "OFFHOOK"
        and user == c.caller
    ):
        s.action(actions, "DIAL_TONE", user=c.caller)
        s.arm(c, "DIAL", 5000)
        return

    # 3. COLLECTING状态下只接受主叫输入的数字
    if (
        c.state == "COLLECTING"
        and kind == "DIGIT"
        and user == c.caller
    ):
        digit = e.get("value")

        # 收到数字后停止拨号音
        s.action(actions, "STOP_DIAL_TONE", user=c.caller)

        # 非字符串输入视为非法号码
        if not isinstance(digit, str):
            s.finish(c, "INVALID")
            s.action(actions, "FAIL_TONE", user=c.caller)
            return

        c.digits += digit
        result = analyze_number(c.digits, s.numbers, c.caller)

        # 号码还未输入完整，继续等待后续数字
        if result == "INCOMPLETE":
            return

        # 非法号码或主叫拨打自己的号码
        if result in ("INVALID", "SELF_CALL"):
            s.finish(c, result)
            s.action(actions, "FAIL_TONE", user=c.caller)
            return

        # 完整的本地号码
        if result == "LOCAL":
            # 被叫忙、被占用或者仍处于等待挂机状态
            if not s.reserve(c, c.digits):
                s.finish(c, "USER_BUSY")
                s.action(actions, "BUSY_TONE", user=c.caller)
                return

            # 预留成功，取消收号定时器并开始振铃
            s.cancel(c)
            c.state = "RINGING"
            s.arm(c, "RING", 10000)

            s.action(actions, "RING", user=c.callee)
            s.action(actions, "RINGBACK", user=c.caller)
            return

    # 4. 呼叫相关用户挂机
    if (
        kind == "ONHOOK"
        and user in (c.caller, c.callee)
        and c.state in ("COLLECTING", "RINGING", "CONNECTED")
    ):
        if c.state == "CONNECTED":
            reason = "NORMAL_CLEAR"
        else:
            reason = "CALLER_CANCEL"

        s.finish(c, reason)
        s.action(
            actions,
            "RELEASE",
            caller=c.caller,
            callee=c.callee,
        )