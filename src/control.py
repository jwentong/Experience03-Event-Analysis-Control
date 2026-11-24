"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c, e, s, actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    # 1. 处理摘机/挂机事件
    if e['kind'] == 'OFFHOOK':
        if e['user'] == c.caller:
            # 主叫刚摘机
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
            c.state = 'COLLECTING'
        elif e['user'] == c.callee and c.state == 'RINGING':
            # 被叫摘机应答
            s.cancel(c)
            if s.activate(c):
                c.state = 'CONNECTED'
                s.action(actions, 'STOP_RING')
                s.action(actions, 'CONNECT')
            else:
                s.finish(c, 'NETWORK_BUSY')
                s.action(actions, 'FAIL_TONE')
                
    elif e['kind'] == 'ONHOOK':
        if c.state == 'CONNECTED':
            s.finish(c, 'NORMAL_CLEAR')
            s.action(actions, 'RELEASE')
        elif c.state in ('COLLECTING', 'RINGING'):
            s.finish(c, 'CALLER_CANCEL')
            s.action(actions, 'RELEASE')

    # 2. 处理拨号事件
    elif e['kind'] == 'DIGIT':
        if e['user'] == c.caller and c.state == 'COLLECTING':
            if not c.digits:
                s.action(actions, 'STOP_DIAL_TONE')
            
            c.digits += str(e['value'])
            res = analyze_number(c.digits, s.numbers, c.caller)
            
            if res == 'INCOMPLETE':
                pass # 继续收号
            elif res in ('INVALID', 'SELF_CALL'):
                s.finish(c, res)
                s.action(actions, 'FAIL_TONE')
            elif res == 'LOCAL':
                if s.reserve(c, c.digits):
                    s.cancel(c)
                    c.state = 'RINGING'
                    s.arm(c, 'RING', 10000)
                    s.action(actions, 'RING')
                    s.action(actions, 'RINGBACK')
                else:
                    s.finish(c, 'USER_BUSY')
                    s.action(actions, 'BUSY_TONE')