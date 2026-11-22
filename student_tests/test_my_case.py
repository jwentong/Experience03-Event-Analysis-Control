"""补充边界反例：总超时、过期事件、等待挂机、帧延迟与同刻顺序。"""
from copy import deepcopy

from src.control import handle_call_event
from src.numbering import analyze_number
from src.runtime import Exchange
from src.scenarios import connected, dial
from src.switch_engine import exchange_frame, run_frames, sample_frame
from src.timeouts import handle_timeout


def test_digits_do_not_extend_total_dial_timeout():
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    for time, digit in [(1000, '1'), (3000, '0'), (4999, '0')]:
        s.enqueue(time, 'DIGIT', '1001', digit)
    s.run(5000)
    c = s.calls['C1']
    assert (c.digits, c.state, c.reason) == ('100', 'ENDED', 'DIAL_TIMEOUT')
    assert not s.owners and s.waiting == {'1001'}


def test_current_token_with_wrong_kind_or_call_is_ignored():
    s = Exchange()
    dial(s)
    s.run(400)
    c = s.calls['C1']
    before = (deepcopy(vars(c)), s.owners.copy(), s.waiting.copy(), list(s.queue))
    actions = []
    for call_id, value in [(c.call_id, 'DIAL'), ('another-call', 'RING')]:
        handle_timeout(c, dict(kind='TIMEOUT', call_id=call_id,
                              token=c.timer, value=value), s, actions)
    assert (vars(c), s.owners, s.waiting, s.queue) == before
    assert actions == [] and not s.tables.pairs


def test_other_user_digit_cannot_change_call():
    s = Exchange()
    dial(s)
    s.run(0)
    c = s.calls['C1']
    actions = []
    handle_call_event(c, dict(kind='DIGIT', user='1003', value='9'), s, actions)
    assert c.digits == '' and c.state == 'COLLECTING' and actions == []


def test_waiting_user_is_not_a_free_callee():
    s = connected()
    s.enqueue(1000, 'ONHOOK', '1001')
    dial(s, '1003', '1002', 1100)
    s.run(1500)
    assert s.calls['C2'].reason == 'USER_BUSY'
    assert s.hooks['1002'] == 1 and '1002' in s.waiting
    assert not s.tables.pairs and not s.owners


def test_frame_delay_and_idle_bytes_after_release():
    s = connected()
    frame = sample_frame(0)
    result = run_frames([frame], s.tables)[0]
    assert result['input_frame_id'] == 0 and result['available_frame_id'] == 1
    assert (int(frame[0, 1]), int(frame[0, 2])) == (3, 6)
    assert (int(result['output'][0, 1]), int(result['output'][0, 2])) == (6, 3)
    s.enqueue(1000, 'ONHOOK', '1001')
    s.run(1000)
    output = exchange_frame(frame, s.tables)
    assert (int(output[0, 1]), int(output[0, 2])) == (0xD5, 0xD5)


def test_timeout_wins_when_queued_before_same_time_answer():
    s = Exchange()
    dial(s)
    s.run(400)  # 振铃定时器已入队，再安排同刻应答。
    s.enqueue(10400, 'OFFHOOK', '1002')
    s.run(10400)
    assert s.calls['C1'].reason == 'NO_ANSWER'
    assert s.calls['C2'].caller == '1002' and s.calls['C2'].state == 'COLLECTING'
    assert not s.tables.pairs


def test_connected_call_ignores_old_timers_without_releasing_bytes():
    s = connected()
    before = exchange_frame(sample_frame(7), s.tables).copy()
    s.run()
    assert s.calls['C1'].state == 'CONNECTED'
    assert (exchange_frame(sample_frame(7), s.tables) == before).all()
    stale = [row for row in s.logs if row['event']['kind'] == 'TIMEOUT']
    assert len(stale) == 2
    assert all(row['before'] == row['after'] == 'CONNECTED'
               and row['actions'] == [] for row in stale)


def test_unicode_digits_and_nonconfigured_prefix_are_invalid():
    assert analyze_number('１００２', ['1001', '1002'], '1001') == 'INVALID'
    assert analyze_number('1', ['2001', '2002'], '2001') == 'INVALID'
    assert analyze_number('200', ['2001', '2002'], '2001') == 'INCOMPLETE'
