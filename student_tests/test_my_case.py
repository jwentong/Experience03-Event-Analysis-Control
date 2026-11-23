"""自拟用例：号码错误结束呼叫后，仍摘机的主叫必须真实挂机才能再次呼出。"""
from src.runtime import Exchange
from src.scenarios import dial

def test_invalid_then_reuse_after_hangup():
    s=Exchange();dial(s,number='1009');s.run()
    assert s.calls['C1'].digits=='1009' and s.calls['C1'].reason=='INVALID' and s.waiting=={'1001'} and not s.tables.pairs
    s.enqueue(5100,'ONHOOK','1001');s.enqueue(5200,'OFFHOOK','1001');s.run(5300)
    assert s.calls['C2'].state=='COLLECTING' and not s.waiting
