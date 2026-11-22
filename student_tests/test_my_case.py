"""自拟测试：收号定时器不重置、振铃起始时刻、字节双向交换与释放清空、异常输入。"""
import pytest

from src.runtime import Exchange
from src.scenarios import dial
from src.switch_engine import sample_frame, exchange_frame
from src.hooks import detect_hook_events
from src.numbering import analyze_number


def test_dial_timer_not_reset_by_digits():
    """收号总超时从摘机起5000ms，拨数字不重置定时器；振铃定时器在10400ms到期。"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.run(0)
    for i, d in enumerate('1002'):
        s.enqueue(100 * (i + 1), 'DIGIT', '1001', d)
    s.run(400)
    timeouts = {(t, e['value']) for t, _, e in s.queue if e['kind'] == 'TIMEOUT'}
    assert timeouts == {(5000, 'DIAL'), (10400, 'RING')}


def test_ringing_starts_at_400():
    """第四位拨号完成时立刻振铃：RING与RINGBACK动作出现在400ms。"""
    s = Exchange()
    dial(s)
    s.run(400)
    ring_rows = [r for r in s.logs if {'RING', 'RINGBACK'} <= {a['type'] for a in r['actions']}]
    assert ring_rows and ring_rows[0]['time_ms'] == 400
    assert ring_rows[0]['after'] == 'RINGING' and s.owners.get('1002') == 'C1'
    assert not s.tables.pairs


def test_bidirectional_bytes_then_release_clears_tables():
    """接通后帧0的TS1=3、TS2=6互换（输出晚一帧）；释放后T/S控制表清空。"""
    s = Exchange()
    dial(s)
    s.enqueue(800, 'OFFHOOK', '1002')
    s.run(900)
    x = sample_frame(0)
    y = exchange_frame(x, s.tables)
    assert y[0, 1] == x[0, 2] == 6
    assert y[0, 2] == x[0, 1] == 3
    s.enqueue(1000, 'ONHOOK', '1001')
    s.run()
    assert not s.tables.pairs and s.tables.t_maps == [{}, {}] and s.tables.s_map == {}


def test_numbering_extended_cases():
    """号码分析补充用例：前缀、局外完整号、非法字符、超长。"""
    plan = ['1001', '1002', '1003', '1004']
    assert analyze_number('100', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('1000', plan, '1001') == 'INVALID'
    assert analyze_number('100x', plan, '1001') == 'INVALID'
    assert analyze_number('12345', plan, '1001') == 'INVALID'
    assert analyze_number('2002', ['2001', '2002'], '2001') == 'LOCAL'


def test_hook_events_sorted_and_error():
    """摘挂机检测按用户编号排序；用户集合不一致抛ValueError。"""
    prev = {'1003': 0, '1001': 0}
    cur = {'1003': 1, '1001': 1}
    assert detect_hook_events(prev, cur) == [
        {'user': '1001', 'kind': 'OFFHOOK'},
        {'user': '1003', 'kind': 'OFFHOOK'},
    ]
    with pytest.raises(ValueError):
        detect_hook_events({'1001': 0}, {'1002': 0})
