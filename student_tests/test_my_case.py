from src.numbering import analyze_number
from src.runtime import Exchange
from src.scenarios import dial

def test_my_custom_case():
    # 测试号码分析
    plan = ['1001', '1002']
    assert analyze_number('1', plan, '1001') == 'INCOMPLETE'
    assert analyze_number('1003', plan, '1001') == 'INVALID'
    assert analyze_number('1002', plan, '1001') == 'LOCAL'
    assert analyze_number('1001', plan, '1001') == 'SELF_CALL'
    
    # 测试呼叫超时
    s = Exchange()
    s.enqueue(0, 'OFFHOOK', '1001')
    s.run()
    assert s.calls['C1'].state == 'ENDED'
    assert s.calls['C1'].reason == 'DIAL_TIMEOUT'