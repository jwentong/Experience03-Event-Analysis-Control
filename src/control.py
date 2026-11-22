"""学生任务：按README状态表修改Call并调用框架服务；收号、忙、振铃、应答、释放；原地修改Call并通过服务调用真实话路。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state=='ENDED':
        return
    kind=e['kind']
    if kind=='OFFHOOK' and e['user']==c.caller and c.state=='COLLECTING':
        s.action(actions,'DIAL_TONE')
        s.arm(c,'DIAL',5000)
    elif kind=='DIGIT' and c.state=='COLLECTING' and e['user']==c.caller:
        c.digits+=e['value']
        result=analyze_number(c.digits,s.numbers,c.caller)
        s.action(actions,'STOP_DIAL_TONE')
        if result=='INCOMPLETE':
            return
        if result in ('INVALID','SELF_CALL'):
            s.action(actions,'FAIL_TONE',reason=result)
            s.finish(c,result)
            return
        if s.reserve(c,c.digits):
            s.cancel(c)
            c.state='RINGING'
            s.action(actions,'RING',user=c.callee)
            s.action(actions,'RINGBACK',user=c.caller)
            s.arm(c,'RING',10000)
        else:
            s.action(actions,'BUSY_TONE')
            s.finish(c,'USER_BUSY')
    elif kind=='OFFHOOK' and c.state=='RINGING' and e['user']==c.callee:
        s.cancel(c)
        if s.activate(c):
            c.state='CONNECTED'
            s.action(actions,'STOP_RING')
            s.action(actions,'CONNECT')
        else:
            s.action(actions,'FAIL_TONE',reason='NETWORK_BUSY')
            s.finish(c,'NETWORK_BUSY')
    elif kind=='ONHOOK' and e['user']==c.caller and c.state in ('COLLECTING','RINGING'):
        s.action(actions,'RELEASE')
        s.finish(c,'CALLER_CANCEL')
    elif kind=='ONHOOK' and c.state=='CONNECTED' and e['user'] in (c.caller,c.callee):
        s.action(actions,'RELEASE')
        s.finish(c,'NORMAL_CLEAR')
