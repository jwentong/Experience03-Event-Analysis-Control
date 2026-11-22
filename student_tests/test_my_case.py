"""自拟测试：只接受主叫在收号状态输入的数字；未接通就挂机后，原呼叫必须真正结束。

手算：
  1) 0ms 1001 摘机，50ms 由 1002 送一个 DIGIT "1"。1002 不是本呼叫主叫，
     该事件不得写入 C1.digits，C1 仍应停在 COLLECTING。
  2) 0~400ms 1001 拨 1002，600ms 主叫挂机（振铃中），800ms 1002 摘机。
     主叫先挂机应置 CALLER_CANCEL 并释放被叫；之后 1002 摘机属于新事件，
     应创建新呼叫，而不能把旧呼叫接成 CONNECTED。
"""
from src.runtime import Exchange
from src.scenarios import dial


def test_digit_from_non_caller_is_ignored():
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(50, 'DIGIT', '1002', '1')
    s.run(50)
    call = s.calls['C1']
    assert call.caller == '1001'
    assert call.digits == ''
    assert call.state == 'COLLECTING'


def test_caller_hangup_before_answer_ends_call():
    s = Exchange()
    dial(s)                                  # 1001 -> 1002，400ms 开始振铃
    s.enqueue(600, 'ONHOOK', '1001')         # 振铃中主叫挂机
    s.enqueue(800, 'OFFHOOK', '1002')        # 被叫随后摘机
    s.run(900)                               # 只跑到 900ms，避免新呼叫的收号超时干扰

    assert s.calls['C1'].state == 'ENDED'
    assert s.calls['C1'].reason == 'CALLER_CANCEL'
    assert not s.tables.pairs                # 没有残留的双向话路
    assert '1002' not in s.waiting           # 挂机后才摘机，不应被留在等待集合
    assert 'C2' in s.calls                   # 被叫摘机构成一个新的呼叫
    assert s.calls['C2'].caller == '1002'
    assert s.calls['C2'].state == 'COLLECTING'

