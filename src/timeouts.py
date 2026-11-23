"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    # 旧定时器或类型不匹配：保持状态、话路和资源不变
    if e['token'] != c.timer or e['value'] != c.timer_kind:
        return
    kind=e['value']
    if kind=='DIAL' and c.state=='COLLECTING':
        s.finish(c,'DIAL_TIMEOUT')
        s.action(actions,'FAIL_TONE')
    elif kind=='RING' and c.state=='RINGING':
        s.cancel(c)
        s.finish(c,'NO_ANSWER')
        s.action(actions,'STOP_RING')
        s.action(actions,'FAIL_TONE')
    # 其它状态（CONNECTED/ENDED等）下的超时直接忽略
