"""学生任务：校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""


def handle_timeout(c,e,s,actions):
    """校验token、timer_kind和当前状态，处理DIAL_TIMEOUT/NO_ANSWER；旧定时器不得影响已接通或结束呼叫。"""
    # 先校验定时器代次token与类型timer_kind：旧token或类型不符直接忽略，
    # 不变更状态、话路和资源（arm/cancel都会使旧token失配）
    if e.get('token')!=c.timer or e.get('value')!=c.timer_kind:
        return
    kind=e.get('value')
    if kind=='DIAL' and c.state=='COLLECTING':
        # 收号超时：未拨完完整号码
        s.finish(c,'DIAL_TIMEOUT')
        s.action(actions,'FAIL_TONE',reason='DIAL_TIMEOUT')
        return
    if kind=='RING' and c.state=='RINGING':
        # 振铃超时：被叫未应答
        s.action(actions,'STOP_RING')
        s.finish(c,'NO_ANSWER')
        s.action(actions,'FAIL_TONE',reason='NO_ANSWER')
        return
