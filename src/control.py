"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

# 收号总超时从摘机起 5000ms（输入数字不重置）；振铃超时从开始振铃起 10000ms
DIAL_TIMEOUT_MS=5000
RING_TIMEOUT_MS=10000


def handle_call_event(c,e,s,actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    kind=e.get('kind')
    user=e.get('user')

    # 已结束的呼叫：后续无关事件一律不再改状态、原因或资源
    if c.state=='ENDED':
        return

    if kind=='OFFHOOK':
        if c.state=='COLLECTING' and user==c.caller:
            # 新呼叫（框架已创建Call并置COLLECTING）：发拨号音，arm收号定时器
            s.action(actions,'DIAL_TONE')
            s.arm(c,'DIAL',DIAL_TIMEOUT_MS)
            return
        if c.state=='RINGING' and user==c.callee:
            # 被叫应答：先取消振铃定时器，再activate建立双向真实话路
            s.cancel(c)
            if s.activate(c):
                c.state='CONNECTED'
                s.action(actions,'STOP_RING')
                s.action(actions,'CONNECT')
            else:
                # 实验二网络拒绝：释放资源并回失败音
                s.finish(c,'NETWORK_BUSY')
                s.action(actions,'STOP_RING')
                s.action(actions,'FAIL_TONE',reason='NETWORK_BUSY')
            return
        # 其他OFFHOOK（例如重复摘机已被框架去重）与本呼叫无关
        return

    if kind=='ONHOOK':
        # 只有本呼叫的主叫/被叫挂机才会被框架路由到这里
        if user in (c.caller,c.callee):
            # 通话中正常拆线；尚未接通（收号/振铃）视为主叫取消
            reason='NORMAL_CLEAR' if c.state=='CONNECTED' else 'CALLER_CANCEL'
            s.finish(c,reason)
            s.action(actions,'RELEASE')
        return

    if kind=='DIGIT':
        # 只接受主叫在COLLECTING状态下输入的号码
        if c.state!='COLLECTING' or user!=c.caller:
            return
        c.digits+=str(e.get('value'))
        s.action(actions,'STOP_DIAL_TONE')
        verdict=analyze_number(c.digits,s.numbers,c.caller)
        if verdict=='INCOMPLETE':
            return  # 号码仍是合法前缀，继续收号
        if verdict!='LOCAL':
            # INVALID / SELF_CALL：结束呼叫并回失败音，原因即判定结果
            s.finish(c,verdict)
            s.action(actions,'FAIL_TONE',reason=verdict)
            return
        # 完整合法号码：先预留被叫，失败则被叫忙
        if not s.reserve(c,c.digits):
            s.finish(c,'USER_BUSY')
            s.action(actions,'BUSY_TONE')
            return
        # 预留成功：取消收号定时器，进入振铃并arm振铃定时器
        s.cancel(c)
        c.state='RINGING'
        s.arm(c,'RING',RING_TIMEOUT_MS)
        s.action(actions,'RING',user=c.callee)
        s.action(actions,'RINGBACK',user=c.caller)
        return
