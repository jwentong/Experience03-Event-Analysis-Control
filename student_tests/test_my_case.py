"""自拟测试：验证摘挂机检测、号码分析与一次完整呼叫的建立和释放。"""
from src.hooks import detect_hook_events
from src.numbering import analyze_number
from src.runtime import Exchange
from src.scenarios import dial, connected


def test_hook_events():
    assert detect_hook_events({'1001': 0}, {'1001': 1}) == [{'user': '1001', 'kind': 'OFFHOOK'}]
    assert detect_hook_events({'1001': 1}, {'1001': 0}) == [{'user': '1001', 'kind': 'ONHOOK'}]
    assert detect_hook_events({'1001': 1}, {'1001': 1}) == []


def test_number_analysis():
    plan = ['1001', '1002', '1003', '1004']
    assert analyze_number('100', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('1002', plan, '1001') == 'LOCAL'
    assert analyze_number('1001', plan, '1001') == 'SELF_CALL'
    assert analyze_number('10022', plan, '1001') == 'INVALID'


def test_full_call_and_release():
    s = connected()
    assert s.calls['C1'].state == 'CONNECTED' and len(s.tables.pairs) == 1
    s.enqueue(1000, 'ONHOOK', '1001')
    s.run()
    assert s.calls['C1'].state == 'ENDED' and not s.tables.pairs
