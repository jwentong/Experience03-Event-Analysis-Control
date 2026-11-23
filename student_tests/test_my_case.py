"""学生自拟反例：号码边界和过期收号定时器。"""
from src.numbering import analyze_number
from src.scenarios import connected


def test_number_analysis_boundaries():
    plan = ['1001', '1002', '1003', '1004']

    assert analyze_number('', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('100', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('1002', plan, '1001') == 'LOCAL'
    assert analyze_number('1001', plan, '1001') == 'SELF_CALL'
    assert analyze_number('9999', plan, '1001') == 'INVALID'
    assert analyze_number('10022', plan, '1001') == 'INVALID'
    assert analyze_number('10a2', plan, '1001') == 'INVALID'


def test_stale_dial_timer_after_answer_is_ignored():
    s = connected()
    assert s.calls['C1'].state == 'CONNECTED'
    assert len(s.tables.pairs) == 1

    s.run()

    assert s.calls['C1'].state == 'CONNECTED'
    assert len(s.tables.pairs) == 1
    stale = [
        row for row in s.logs
        if row['event']['kind'] == 'TIMEOUT'
        and row['event'].get('value') == 'DIAL'
        and row['time_ms'] == 5000
    ]
    assert stale
    assert all(row['before'] == 'CONNECTED' and row['after'] == 'CONNECTED' for row in stale)
