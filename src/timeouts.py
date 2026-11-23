"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if e['token']!=c.timer:
        return
    if e['value']!=c.timer_kind:
        return
    if e['value']=='DIAL' and c.state=='COLLECTING':
        s.finish(c,'DIAL_TIMEOUT')
        s.action(actions,'FAIL_TONE')
    elif e['value']=='RING' and c.state=='RINGING':
        s.action(actions,'STOP_RING')
        s.finish(c,'NO_ANSWER')
        s.action(actions,'FAIL_TONE')
