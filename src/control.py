"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    kind=e['kind']
    if kind=='OFFHOOK':
        if c.state=='RINGING':
            # 被叫应答：取消振铃定时器，激活话路
            s.cancel(c)
            if s.activate(c):
                c.state='CONNECTED'
                s.action(actions,'STOP_RING')
                s.action(actions,'CONNECT')
            else:
                s.finish(c,'NETWORK_BUSY')
                s.action(actions,'FAIL_TONE')
        else:
            # 空闲用户摘机，框架已创建Call并置COLLECTING
            s.action(actions,'DIAL_TONE')
            s.arm(c,'DIAL',5000)
    elif kind=='DIGIT':
        # 仅主叫在收号态输入
        if c.state!='COLLECTING' or e.get('user')!=c.caller:
            return
        c.digits+=e['value']
        result=analyze_number(c.digits,s.numbers,c.caller)
        if result in ('INVALID','SELF_CALL'):
            s.finish(c,result)
            s.action(actions,'FAIL_TONE')
        elif result=='INCOMPLETE':
            s.action(actions,'STOP_DIAL_TONE')
        elif result=='LOCAL':
            s.cancel(c)
            if not s.reserve(c,c.digits):
                s.finish(c,'USER_BUSY')
                s.action(actions,'BUSY_TONE')
            else:
                c.state='RINGING'
                s.arm(c,'RING',10000)
                s.action(actions,'RING')
                s.action(actions,'RINGBACK')
    elif kind=='ONHOOK':
        if c.state=='CONNECTED':
            s.finish(c,'NORMAL_CLEAR')
            s.action(actions,'RELEASE')
        elif c.state in ('RINGING','COLLECTING'):
            s.finish(c,'CALLER_CANCEL')
            s.action(actions,'RELEASE')
        # 其它状态（如ENDED）保持不变
