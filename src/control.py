"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

DIAL_TOTAL_MS=5000
RING_TOTAL_MS=10000

def _dial_plan(s):
    """拨号计划取自交换机配置，避免把号码硬编码在控制逻辑里。"""
    numbers=getattr(s,'numbers',None)
    return list(numbers) if numbers else []

def _offhook(c,user,s,actions):
    if c.state=='COLLECTING':
        # 摘机建呼叫：只有主叫的第一次摘机启动收号，重复采样由框架去重。
        if user==c.caller and c.timer==0 and not c.digits:
            s.action(actions,'DIAL_TONE')
            s.arm(c,'DIAL',DIAL_TOTAL_MS)
        return
    if c.state=='RINGING':
        if user!=c.callee:
            return
        # 被叫摘机只代表应答动作，真正接通要以activate建立双向T/S映射为准。
        s.cancel(c)
        if s.activate(c):
            c.state='CONNECTED'
            s.action(actions,'STOP_RING')
            s.action(actions,'CONNECT')
        else:
            s.finish(c,'NETWORK_BUSY')
            s.action(actions,'FAIL_TONE')

def _onhook(c,user,s,actions):
    if user not in (c.caller,c.callee):
        return
    if c.callee is None and user!=c.caller:
        return
    # 通话中挂机是正常拆线，振铃/收号阶段挂机是主叫取消。
    reason='NORMAL_CLEAR' if c.state=='CONNECTED' else 'CALLER_CANCEL'
    s.action(actions,'RELEASE')
    s.finish(c,reason)

def _digit(c,user,value,s,actions):
    if c.state!='COLLECTING' or user!=c.caller:
        return
    if not isinstance(value,str) or len(value)!=1:
        return
    c.digits+=value
    result=analyze_number(c.digits,_dial_plan(s),c.caller)
    if result=='INCOMPLETE':
        # 收到有效前缀后拨号音即可停止，继续等待后续号码。
        s.action(actions,'STOP_DIAL_TONE')
        return
    if result in ('INVALID','SELF_CALL'):
        s.finish(c,result)
        s.action(actions,'FAIL_TONE')
        return
    # 完整合法号码：先预留被叫资源，失败即被叫忙。
    if not s.reserve(c,c.digits):
        s.finish(c,'USER_BUSY')
        s.action(actions,'BUSY_TONE')
        return
    # 预留成功后收号任务结束，改为振铃阶段并重新武装振铃定时器。
    s.cancel(c)
    c.state='RINGING'
    s.arm(c,'RING',RING_TOTAL_MS)
    s.action(actions,'RING')
    s.action(actions,'RINGBACK')

def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state=='ENDED':
        return
    kind=e.get('kind')
    user=e.get('user')
    if kind=='OFFHOOK':
        _offhook(c,user,s,actions)
    elif kind=='ONHOOK':
        _onhook(c,user,s,actions)
    elif kind=='DIGIT':
        _digit(c,user,e.get('value'),s,actions)
