"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    kind=e['kind']

    if kind=='OFFHOOK':
        if c.state=='COLLECTING':
            s.action(actions,'DIAL_TONE')
            s.arm(c,'DIAL',5000)
        elif c.state=='RINGING' and e['user']==c.callee:
            s.cancel(c)
            if s.activate(c):
                c.state='CONNECTED'
                s.action(actions,'STOP_RING')
                s.action(actions,'CONNECT')
            else:
                s.finish(c,'NETWORK_BUSY')
                s.action(actions,'FAIL_TONE')
        return

    if kind=='DIGIT':
        if c.state!='COLLECTING' or e['user']!=c.caller:
            return
        s.action(actions,'STOP_DIAL_TONE')
        c.digits+=e['value']
        verdict=analyze_number(c.digits,s.numbers,c.caller)
        if verdict=='INCOMPLETE':
            return
        if verdict in ('INVALID','SELF_CALL'):
            s.finish(c,verdict)
            s.action(actions,'FAIL_TONE')
            return
        if not s.reserve(c,c.digits):
            s.finish(c,'USER_BUSY')
            s.action(actions,'BUSY_TONE')
            return
        s.cancel(c)
        c.state='RINGING'
        s.arm(c,'RING',10000)
        s.action(actions,'RING')
        s.action(actions,'RINGBACK')
        return

    if kind=='ONHOOK':
        if c.state not in ('COLLECTING','RINGING','CONNECTED'):
            return
        reason='NORMAL_CLEAR' if c.state=='CONNECTED' else 'CALLER_CANCEL'
        s.finish(c,reason)
        s.action(actions,'RELEASE')
