"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""


def handle_timeout(c, e, s, actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if c.state == 'ENDED':
        return
    if e.get('call_id') != c.call_id:
        return
    # token 每次 arm/cancel 都会递增，旧定时器带的是旧代次
    if e.get('token') != c.timer:
        return
    if e.get('value') != c.timer_kind:
        return

    kind = e.get('value')
    if kind == 'DIAL' and c.state == 'COLLECTING':
        s.finish(c, 'DIAL_TIMEOUT')
        s.action(actions, 'FAIL_TONE')
    elif kind == 'RING' and c.state == 'RINGING':
        s.finish(c, 'NO_ANSWER')
        s.action(actions, 'STOP_RING')
        s.action(actions, 'FAIL_TONE')
