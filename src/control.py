"""学生任务：按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
from src.numbering import analyze_number

def handle_call_event(c, e, s, actions):
    """按README状态表修改Call并调用框架服务；收号、忙线、振铃、应答激活真实话路、挂机释放。"""
    
    # 如果通话已经结束，直接忽略后续事件
    if c.state == "ENDED":
        return

    # 0. 主叫刚摘机（初始状态），框架已建好 Call 并把状态设为 COLLECTING
    if e['kind'] == 'OFFHOOK' and c.state == 'COLLECTING' and not c.digits:
        s.action(actions, "DIAL_TONE")
        s.arm(c, "DIAL", 5000)
        return

    # 1. 处理主叫拨号 (DIGIT)
    if e['kind'] == "DIGIT" and c.state == "COLLECTING" and e['user'] == c.caller:
        c.digits += e['value']
        
        # 修正：直接把 4 个用户作为拨号计划传进去
        dial_plan = ["1001", "1002", "1003", "1004"]
        res = analyze_number(c.digits, dial_plan, c.caller)
        
        if res == "INCOMPLETE":
            # 号码还不全，停止拨号音，继续等
            s.action(actions, "STOP_DIAL_TONE")
            
        elif res in ("INVALID", "SELF_CALL"):
            # 号码非法或打给自己，直接失败结束
            s.finish(c, res)
            s.action(actions, "FAIL_TONE")
            
        elif res == "LOCAL":
            # 号码完整且合法
            s.cancel(c)  # 取消收号超时定时器
            if s.reserve(c, c.digits):
                # 被叫空闲，预留成功，进入振铃
                c.state = "RINGING"
                s.arm(c, "RING", 10000)  # 挂起 10 秒振铃超时
                s.action(actions, "RING")
                s.action(actions, "RINGBACK")
            else:
                # 被叫忙，无法预留
                s.finish(c, "USER_BUSY")
                s.action(actions, "BUSY_TONE")

    # 2. 处理被叫摘机接听 (OFFHOOK)
    elif e['kind'] == "OFFHOOK" and c.state == "RINGING" and e['user'] == c.callee:
        s.cancel(c)  # 取消振铃超时定时器
        if s.activate(c):
            # 成功接通双向话路
            c.state = "CONNECTED"
            s.action(actions, "STOP_RING")
            s.action(actions, "CONNECT")
        else:
            # 网络资源不足，接通失败
            s.finish(c, "NETWORK_BUSY")
            s.action(actions, "FAIL_TONE")

    # 3. 处理挂机 (ONHOOK)
    elif e['kind'] == "ONHOOK":
        if c.state == "CONNECTED":
            # 通话中挂机，正常释放
            s.finish(c, "NORMAL_CLEAR")
            s.action(actions, "RELEASE")
        elif c.state in ("COLLECTING", "RINGING"):
            # 还没接通就挂机了（主叫取消或拒绝接听）
            s.finish(c, "CALLER_CANCEL")
            s.action(actions, "RELEASE")