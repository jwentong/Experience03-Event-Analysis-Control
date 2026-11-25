"""自拟反例：振铃期取消、忙时保持原呼叫、旧定时器与号码边界。"""
from src.runtime import Exchange
from src.scenarios import dial, connected
from src.switch_engine import sample_frame, exchange_frame
from src.switch_models import IDLE
from src.hooks import detect_hook_events
from src.numbering import analyze_number


def test_cancel_ringing_releases_slots_to_idle():
    s = Exchange()
    dial(s)
    s.enqueue(600, 'ONHOOK', '1001')
    s.run()
    assert s.calls['C1'].reason == 'CALLER_CANCEL'
    assert not s.tables.pairs and not s.owners
    y = exchange_frame(sample_frame(0), s.tables)
    assert int(y[0, 1]) == IDLE and int(y[0, 2]) == IDLE


def test_busy_callee_keeps_connected_call():
    s = connected()
    dial(s, '1003', '1002', 1000)
    s.run()
    assert s.calls['C2'].reason == 'USER_BUSY'
    assert s.calls['C1'].state == 'CONNECTED' and len(s.tables.pairs) == 1
    x = sample_frame(2)
    y = exchange_frame(x, s.tables)
    assert int(y[0, 1]) == int(x[0, 2]) and int(y[0, 2]) == int(x[0, 1])


def test_stale_dial_timeout_ignored_while_ringing():
    s = Exchange()
    dial(s)
    s.run(5000)
    assert s.calls['C1'].state == 'RINGING' and s.calls['C1'].reason == ''


def test_number_analysis_edges():
    plan = ['1001', '1002', '1003', '1004']
    assert analyze_number('', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('1002', plan, '1001') == 'LOCAL'
    assert analyze_number('1001', plan, '1001') == 'SELF_CALL'
    assert analyze_number('10022', plan, '1001') == 'INVALID'


def test_hook_events_sorted_and_pure():
    before = {'1002': 0, '1001': 1}
    after = {'1002': 1, '1001': 0}
    events = detect_hook_events(before, after)
    assert events == [{'user': '1001', 'kind': 'ONHOOK'}, {'user': '1002', 'kind': 'OFFHOOK'}]
    assert before == {'1002': 0, '1001': 1}
