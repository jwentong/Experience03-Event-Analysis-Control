"""自拟测试：验证同一时刻事件顺序、旧定时器忽略、释放后空闲码和输入校验。"""
import pytest
from src.runtime import Exchange
from src.hooks import detect_hook_events
from src.numbering import analyze_number
from src.switch_engine import sample_frame, exchange_frame


def test_same_time_digits_before_dial_timeout():
    """5000ms 时先处理的应是大致预入队的四位 DIGIT，后到的 DIAL 超时因 token 失配被忽略。"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    for digit in '1002':
        s.enqueue(5000, 'DIGIT', '1001', digit)
    s.run(5000)
    c = s.calls['C1']
    assert c.state == 'RINGING'
    assert c.timer_kind == 'RING'
    assert c.reason == ''
    assert s.owners['1002'] == 'C1'


def test_release_restores_idle_bytes():
    """主叫挂机后双向话路释放，交换输出对应时隙回到空闲码 0xD5。"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    for i, digit in enumerate('1002'):
        s.enqueue(100 * (i + 1), 'DIGIT', '1001', digit)
    s.enqueue(800, 'OFFHOOK', '1002')
    s.enqueue(1000, 'ONHOOK', '1001')
    s.run()
    assert s.calls['C1'].state == 'ENDED'
    assert not s.tables.pairs
    out = exchange_frame(sample_frame(2), s.tables)
    assert out[0, 1] == 0xD5 and out[0, 2] == 0xD5
    assert (out[0, 1], out[0, 2]) == (213, 213)


def test_bad_inputs_are_rejected():
    """摘挂机采样非法与号码非法时按规范报错或返回 INVALID。"""
    with pytest.raises(ValueError):
        detect_hook_events({'1001': 0}, {'1002': 0})
    assert analyze_number('10022', ['1001', '1002'], '1001') == 'INVALID'
    assert analyze_number('a', ['1001', '1002'], '1001') == 'INVALID'
    assert analyze_number('2002', ['2001', '2002'], '2001') == 'LOCAL'
