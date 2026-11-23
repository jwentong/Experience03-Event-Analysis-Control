"""自拟测试：收号中途挂机与旧定时器、以及配置驱动号码的前缀判断。"""
from src.runtime import Exchange
from src.numbering import analyze_number


def test_cancel_in_collecting_ignores_old_dial():
    """收号中途主叫挂机后，5000ms 到达的旧收号定时器不得改变已结束呼叫。"""
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.enqueue(100, 'DIGIT', '1001', '1')
    s.enqueue(200, 'ONHOOK', '1001')
    s.run()
    c = s.calls['C1']
    assert c.state == 'ENDED'
    assert c.reason == 'CALLER_CANCEL'
    assert not s.tables.pairs
    assert not s.owners
    assert '1001' not in s.waiting
    stale = [row for row in s.logs if row['event']['kind'] == 'TIMEOUT']
    assert stale, '应保留旧定时器事件在日志中'
    assert all(row['before'] == 'ENDED' and row['after'] == 'ENDED' and row['actions'] == []
               for row in stale)


def test_number_prefix_with_configured_plan():
    """号码分析应跟随配置的拨号计划，而不是硬编码 1001 至 1004。"""
    plan = ['2001', '2002']
    assert analyze_number('200', plan, '2001') == 'INCOMPLETE'
    assert analyze_number('2002', plan, '2001') == 'LOCAL'
    assert analyze_number('2001', plan, '2001') == 'SELF_CALL'
    assert analyze_number('2003', plan, '2001') == 'INVALID'
