"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c, e, s, actions):
    if c.timer != e["token"]:
        return
    if c.state == "ENDED":
        return

    timer_kind = e["value"]
    cur_state = c.state

    if cur_state == "COLLECTING" and timer_kind == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
        c.state = "ENDED"
    elif cur_state == "RINGING" and timer_kind == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")
        c.state = "ENDED"


