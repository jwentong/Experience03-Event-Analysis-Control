"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""

def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    if c.state=='ENDED':
        return
    # 事件必须属于本呼叫：call_id不对说明不是这条话路的定时器。
    if e.get('call_id')!=c.call_id:
        return
    kind=e.get('value')
    token=e.get('token')
    # 双保险：代次token与定时器类别都要与当前呼叫一致，否则是过期定时器，原样忽略。
    if c.timer_kind!=kind or c.timer!=token:
        return
    if kind=='DIAL' and c.state=='COLLECTING':
        s.finish(c,'DIAL_TIMEOUT')
        s.action(actions,'FAIL_TONE')
    elif kind=='RING' and c.state=='RINGING':
        s.finish(c,'NO_ANSWER')
        s.action(actions,'STOP_RING')
        s.action(actions,'FAIL_TONE')
