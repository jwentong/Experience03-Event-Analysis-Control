"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == 'ENDED':
        return
    kind, user = e.get('kind'), e.get('user')
    if user not in (c.caller, c.callee) or user is None:
        return
    if kind == 'ONHOOK':
        reason = 'NORMAL_CLEAR' if c.state == 'CONNECTED' else 'CALLER_CANCEL'
        s.finish(c, reason)
        s.action(actions, 'RELEASE')
        return
    if c.state == 'COLLECTING' and user == c.caller:
        if kind == 'OFFHOOK':
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
        elif kind == 'DIGIT':
            c.digits += e['value']
            s.action(actions, 'STOP_DIAL_TONE')
            result = analyze_number(c.digits, s.numbers, c.caller)
            if result in ('INVALID', 'SELF_CALL'):
                s.finish(c, result)
                s.action(actions, 'FAIL_TONE')
            elif result == 'LOCAL':
                if not s.reserve(c, c.digits):
                    s.finish(c, 'USER_BUSY')
                    s.action(actions, 'BUSY_TONE')
                else:
                    s.cancel(c)
                    c.state = 'RINGING'
                    s.arm(c, 'RING', 10000)
                    s.action(actions, 'RING')
                    s.action(actions, 'RINGBACK')
    elif c.state == 'RINGING' and kind == 'OFFHOOK' and user == c.callee:
        s.cancel(c)
        if s.activate(c):
            c.state = 'CONNECTED'
            s.action(actions, 'STOP_RING')
            s.action(actions, 'CONNECT')
        else:
            s.finish(c, 'NETWORK_BUSY')
            s.action(actions, 'FAIL_TONE')
