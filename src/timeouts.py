"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if c.state == 'ENDED':
        return

    kind = e.get('value')
    if e.get('token') != c.timer or kind != c.timer_kind:
        return

    if c.state == 'COLLECTING' and kind == 'DIAL':
        s.finish(c, 'DIAL_TIMEOUT')
        s.action(actions, 'FAIL_TONE', reason='DIAL_TIMEOUT')
        return

    if c.state == 'RINGING' and kind == 'RING':
        s.finish(c, 'NO_ANSWER')
        s.action(actions, 'STOP_RING')
        s.action(actions, 'FAIL_TONE', reason='NO_ANSWER')
