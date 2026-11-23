"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c, e, s, actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    
    # 1. 如果呼叫已经结束，或者当前没有定时器，直接忽略
    if c.state == "ENDED" or c.timer_kind is None:
        return

    # 2. 校验 token 和定时器类型
    # 注意：框架可能用 e.get('token') 来区分是不是旧定时器
    # 如果事件的 token 与当前的 c.timer 不一致，或者类型不一致，说明是作废的超时事件
    if e.get('token') != c.timer or e.get('value') != c.timer_kind:
        return

    # 3. 处理 DIAL 超时（收号超时）
    if c.state == "COLLECTING" and e.get('value') == "DIAL":
        s.finish(c, "DIAL_TIMEOUT")
        s.action(actions, "FAIL_TONE")
        
    # 4. 处理 RING 超时（无人接听）
    elif c.state == "RINGING" and e.get('value') == "RING":
        s.finish(c, "NO_ANSWER")
        s.action(actions, "STOP_RING")
        s.action(actions, "FAIL_TONE")