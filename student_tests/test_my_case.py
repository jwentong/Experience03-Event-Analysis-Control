"""张志伟 2024280016 的自拟边界测试。"""
from src.runtime import Exchange
from src.scenarios import dial


def test_callee_digit_during_ringing_is_ignored():
    """只有主叫处于 COLLECTING 时才能收号。

    1001 拨完 1002 后进入 RINGING；1002 在振铃期间送入一个 DIGIT。
    该事件可被运行时关联到当前呼叫，但控制函数不得追加 digits，
    也不得改变 RINGING 状态或提前建立话路。
    """
    s = Exchange()
    dial(s, caller='1001', number='1002')
    s.enqueue(500, 'DIGIT', '1002', '9')
    s.run(500)

    call = s.calls['C1']
    assert call.state == 'RINGING'
    assert call.digits == '1002'
    assert call.reason == ''
    assert not s.tables.pairs


def test_incomplete_prefix_times_out_without_ringing():
    """只拨合法前缀 10 时，号码不完整且不得预留被叫。

    收号总超时从摘机时刻开始而不是从最后一个数字重新计时；
    5000 ms 时应以 DIAL_TIMEOUT 结束，1001 仍摘机并等待 ONHOOK，
    1002 不应成为 owner，也不存在双向话路。
    """
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'DIGIT', '1001', '0')
    s.run()

    call = s.calls['C1']
    assert call.reason == 'DIAL_TIMEOUT'
    assert call.state == 'ENDED'
    assert s.waiting == {'1001'}
    assert '1002' not in s.owners
    assert not s.tables.pairs
