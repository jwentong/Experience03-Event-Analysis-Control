"""呼叫超时事件处理。"""


def handle_timeout(c, e, s, actions):
    """校验超时事件，只处理当前呼叫的有效定时器。"""

    # 只处理超时事件
    if e.get("kind") != "TIMEOUT":
        return

    # 呼叫编号不匹配，说明该事件不属于当前呼叫
    if e.get("call_id") != c.call_id:
        return

    # token不一致表示这是已经失效的旧定时器
    if e.get("token") != c.timer:
        return

    timeout_kind = e.get("value")

    # 超时类型必须与当前有效定时器一致
    if timeout_kind != c.timer_kind:
        return

    # 有效的收号超时
    if timeout_kind == "DIAL" and c.state == "COLLECTING":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE", user=c.caller)
        return

    # 有效的振铃超时
    if timeout_kind == "RING" and c.state == "RINGING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING", user=c.callee)
        s.action(actions, "FAIL_TONE", user=c.caller)
        return

    # 定时器类型与当前状态不匹配时直接忽略