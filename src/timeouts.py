"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器直接忽略。"""
    if c.state=='ENDED':
        return
    if e.get('token')!=c.timer or e.get('value')!=c.timer_kind:
        return
    if e['value']=='DIAL' and c.state=='COLLECTING':
        s.action(actions,'FAIL_TONE',reason='DIAL_TIMEOUT')
        s.finish(c,'DIAL_TIMEOUT')
    elif e['value']=='RING' and c.state=='RINGING':
        s.action(actions,'STOP_RING')
        s.action(actions,'FAIL_TONE',reason='NO_ANSWER')
        s.finish(c,'NO_ANSWER')
