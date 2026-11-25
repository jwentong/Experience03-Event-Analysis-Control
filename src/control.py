"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

RING_DELAY_MS = 10000


def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == 'ENDED':
        return
    kind = e['kind']
    if kind == 'OFFHOOK':
        if c.state == 'COLLECTING' and e.get('user') == c.caller:
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
        elif c.state == 'RINGING' and e.get('user') == c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state = 'CONNECTED'
                s.action(actions, 'STOP_RING')
                s.action(actions, 'CONNECT')
            else:
                s.finish(c, 'NETWORK_BUSY')
                s.action(actions, 'FAIL_TONE')
    elif kind == 'DIGIT':
        if c.state != 'COLLECTING' or e.get('user') != c.caller:
            return
        c.digits += str(e['value'])
        verdict = analyze_number(c.digits, s.numbers, c.caller)
        if verdict == 'INCOMPLETE':
            s.action(actions, 'STOP_DIAL_TONE')
        elif verdict in ('INVALID', 'SELF_CALL'):
            s.finish(c, verdict)
            s.action(actions, 'FAIL_TONE')
        else:
            if not s.reserve(c, c.digits):
                s.finish(c, 'USER_BUSY')
                s.action(actions, 'BUSY_TONE')
            else:
                s.cancel(c)
                c.state = 'RINGING'
                s.arm(c, 'RING', RING_DELAY_MS)
                s.action(actions, 'RING')
                s.action(actions, 'RINGBACK')
    elif kind == 'ONHOOK':
        if c.state in ('COLLECTING', 'RINGING'):
            s.finish(c, 'CALLER_CANCEL')
            s.action(actions, 'RELEASE')
        elif c.state == 'CONNECTED':
            s.finish(c, 'NORMAL_CLEAR')
            s.action(actions, 'RELEASE')
