"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if c.state=='ENDED':return
    if e['token']!=c.timer or e['value']!=c.timer_kind:return
    if c.state=='COLLECTING' and c.timer_kind=='DIAL':
        s.finish(c,'DIAL_TIMEOUT');s.action(actions,'FAIL_TONE')
    elif c.state=='RINGING' and c.timer_kind=='RING':
        s.finish(c,'NO_ANSWER');s.action(actions,'STOP_RING');s.action(actions,'FAIL_TONE')
