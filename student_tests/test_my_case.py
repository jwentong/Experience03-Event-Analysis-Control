"""学生自拟测试：调用任务函数与 Exchange，含有效 assert。"""
from src.runtime import Exchange
from src.scenarios import dial
from src.hooks import detect_hook_events
from src.numbering import analyze_number

P = ['1001', '1002', '1003', '1004']


def test_hook_detection_sorted_pure():
    previous = {'1002': 0, '1001': 1}
    current = {'1002': 1, '1001': 0}
    events = detect_hook_events(previous, current)
    assert [x['user'] for x in events] == ['1001', '1002']
    assert events[0]['kind'] == 'ONHOOK'
    assert events[1]['kind'] == 'OFFHOOK'
    # 输入不被修改
    assert previous == {'1002': 0, '1001': 1}
    assert current == {'1002': 1, '1001': 0}


def test_number_boundary():
    assert analyze_number('1002', P, '1001') == 'LOCAL'
    assert analyze_number('1001', P, '1001') == 'SELF_CALL'
    assert analyze_number('9999', P, '1001') == 'INVALID'
    assert analyze_number('1', P, '1001') == 'INCOMPLETE'
    assert analyze_number('', P, '1001') == 'INCOMPLETE'


def test_dial_timeout_releases_owner():
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.run()
    assert s.calls['C1'].reason == 'DIAL_TIMEOUT'
    assert not s.owners
