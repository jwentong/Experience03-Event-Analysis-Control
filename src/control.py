"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c, e, s, actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == 'ENDED':
        return
    kind = e['kind']
    user = e['user']

    if kind == 'OFFHOOK':
        if c.state == 'COLLECTING' and user == c.caller and c.digits == '':
            # 新呼叫：送拨号音，启动收号总超时
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
        elif c.state == 'RINGING' and user == c.callee:
            # 被叫应答：取消振铃定时器，建立真实双向话路
            s.cancel(c)
            if s.activate(c):
                c.state = 'CONNECTED'
                s.action(actions, 'STOP_RING')
                s.action(actions, 'CONNECT')
            else:
                s.finish(c, 'NETWORK_BUSY')
                s.action(actions, 'FAIL_TONE')
        return

    if kind == 'DIGIT':
        if c.state != 'COLLECTING' or user != c.caller:
            return
        c.digits += e['value']
        verdict = analyze_number(c.digits, s.numbers, c.caller)
        if verdict == 'INCOMPLETE':
            s.action(actions, 'STOP_DIAL_TONE')
        elif verdict in ('INVALID', 'SELF_CALL'):
            s.finish(c, verdict)
            s.action(actions, 'FAIL_TONE')
        elif verdict == 'LOCAL':
            if s.reserve(c, c.digits):
                s.cancel(c)
                c.state = 'RINGING'
                s.arm(c, 'RING', 10000)
                s.action(actions, 'RING')
                s.action(actions, 'RINGBACK')
            else:
                s.finish(c, 'USER_BUSY')
                s.action(actions, 'BUSY_TONE')
        return

    if kind == 'ONHOOK':
        if c.state == 'CONNECTED':
            s.finish(c, 'NORMAL_CLEAR')
        else:
            s.finish(c, 'CALLER_CANCEL')
        s.action(actions, 'RELEASE')
        return
