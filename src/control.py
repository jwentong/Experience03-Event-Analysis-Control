"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    if c.state == 'ENDED':
        return

    kind = e.get('kind')

    if kind == 'OFFHOOK':
        if c.state == 'COLLECTING':
            # 主叫刚摘机：送拨号音并启动收号总超时（5000ms，输入数字不重置）
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
            return
        if c.state == 'RINGING' and e.get('user') == c.callee:
            # 被叫摘机才是应答：先取消振铃定时器，再真正建立双向话路
            s.cancel(c)
            if s.activate(c):
                c.state = 'CONNECTED'
                s.action(actions, 'STOP_RING')
                s.action(actions, 'CONNECT')
            else:
                s.finish(c, 'NETWORK_BUSY')
                s.action(actions, 'FAIL_TONE')
            return
        return

    if kind == 'ONHOOK':
        if e.get('user') not in (c.caller, c.callee):
            return
        reason = 'NORMAL_CLEAR' if c.state == 'CONNECTED' else 'CALLER_CANCEL'
        s.finish(c, reason)
        s.action(actions, 'RELEASE')
        return

    if kind == 'DIGIT':
        # 只接受主叫在收号状态输入的一位数字
        if c.state != 'COLLECTING' or e.get('user') != c.caller:
            return
        c.digits += str(e.get('value'))
        result = analyze_number(c.digits, s.numbers, c.caller)

        if result == 'INCOMPLETE':
            s.action(actions, 'STOP_DIAL_TONE')
            return
        if result in ('INVALID', 'SELF_CALL'):
            s.finish(c, result)
            s.action(actions, 'FAIL_TONE')
            return
        if result == 'LOCAL':
            # 号码完整：先停收号定时器，再尝试预留被叫
            s.cancel(c)
            if not s.reserve(c, c.digits):
                s.finish(c, 'USER_BUSY')
                s.action(actions, 'BUSY_TONE')
                return
            c.state = 'RINGING'
            s.arm(c, 'RING', 10000)
            s.action(actions, 'RING')
            s.action(actions, 'RINGBACK')
            return
        return
