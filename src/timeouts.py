"""超时处理：先校验 token 与 timer_kind，再按当前状态处理有效超时。"""


def handle_timeout(c, e, s, actions):
    # 第一道：token 代次必须等于当前代次，旧定时器直接忽略
    if e.get("token") != c.timer:
        return

    # 第二道：定时器类型必须匹配（DIAL 只处理收号超时，RING 只处理振铃超时）
    if e.get("value") != c.timer_kind:
        return

    # 第三道：已经结束的呼叫不再响应任何超时
    if c.state == "ENDED":
        return

    kind = e["value"]
    if kind == "DIAL" and c.state == "COLLECTING":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
        return

    if kind == "RING" and c.state == "RINGING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")
