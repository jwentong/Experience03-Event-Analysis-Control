"""
实验三 自定义测试用例  student_tests/test_my_case.py
覆盖核心场景：摘机拨号、号码收号、振铃应答、挂机释放、超时处理、忙线、自呼叫、旧定时器
"""
from src.runtime import Exchange


def test_offhook_dial_tone():
    """主叫摘机 → 进入收号状态，播放拨号音"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.run(0)
    assert s.calls['C1'].state == 'COLLECTING'
    assert s.logs[0]['actions'][0]['type'] == 'DIAL_TONE'


def test_dial_complete_ringing():
    """拨完完整合法号码 → 进入振铃状态，播放回铃音"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.run(500)
    assert s.calls['C1'].state == 'RINGING'
    action_types = {a['type'] for a in s.logs[-1]['actions']}
    assert 'RING' in action_types
    assert 'RINGBACK' in action_types


def test_callee_answer_connect():
    """被叫摘机应答 → 通话接通，双向连接建立"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.enqueue(800, 'OFFHOOK', '1002')
    s.run(900)
    assert s.calls['C1'].state == 'CONNECTED'
    assert len(s.tables.pairs) == 1


def test_caller_onhook_release():
    """通话中主叫挂机 → 正常释放，连接断开"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.enqueue(800, 'OFFHOOK', '1002')
    s.enqueue(1000, 'ONHOOK', '1001')
    s.run(1100)
    assert s.calls['C1'].state == 'ENDED'
    assert not s.tables.pairs


def test_callee_onhook_release():
    """通话中被叫挂机 → 正常释放"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.enqueue(800, 'OFFHOOK', '1002')
    s.enqueue(1000, 'ONHOOK', '1002')
    s.run(1100)
    assert s.calls['C1'].state == 'ENDED'
    assert not s.tables.pairs


def test_dial_timeout():
    """拨号超时 → 结束呼叫，原因为DIAL_TIMEOUT"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.run(5000)
    assert s.calls['C1'].reason == 'DIAL_TIMEOUT'
    assert s.calls['C1'].state == 'ENDED'


def test_ring_timeout():
    """振铃超时无人接听 → 结束呼叫，原因为NO_ANSWER"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.run(10400)
    assert s.calls['C1'].reason == 'NO_ANSWER'
    assert s.calls['C1'].state == 'ENDED'


def test_busy_line():
    """被叫占线 → 返回忙音，原因为USER_BUSY"""
    s = Exchange()
    # 先让1002处于通话中
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.enqueue(800, 'OFFHOOK', '1002')
    # 再用1003拨打1002
    s.enqueue(1000, 'OFFHOOK', '1003')
    s.enqueue(1100, 'DIGIT', '1003', '1')
    s.enqueue(1200, 'DIGIT', '1003', '0')
    s.enqueue(1300, 'DIGIT', '1003', '0')
    s.enqueue(1400, 'DIGIT', '1003', '2')
    s.run(1500)
    assert s.calls['C2'].reason == 'USER_BUSY'
    assert s.calls['C2'].state == 'ENDED'


def test_self_call_reject():
    """拨打自己号码 → 拒绝呼叫"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '1')
    s.run(500)
    assert s.calls['C1'].reason == 'SELF_CALL'
    assert s.calls['C1'].state == 'ENDED'


def test_old_timer_not_affect_connected():
    """接通后旧振铃定时器触发 → 不打断通话"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.enqueue(300, 'DIGIT', '1001', '0')
    s.enqueue(400, 'DIGIT', '1001', '2')
    s.enqueue(800, 'OFFHOOK', '1002')
    # 模拟10000ms旧振铃超时到达
    s.run(10000)
    assert s.calls['C1'].state == 'CONNECTED'
    assert len(s.tables.pairs) == 1
