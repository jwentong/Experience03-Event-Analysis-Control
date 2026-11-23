"""自拟测试：覆盖号码分析边界、摘挂机排序，以及“等待挂机用户不可被叫”的忙线场景。"""
from src.numbering import analyze_number
from src.hooks import detect_hook_events
from src.runtime import Exchange
from src.scenarios import dial,connected
P=['1001','1002','1003','1004']

def test_numbering_boundaries():
    assert analyze_number('10',P,'1001')=='INCOMPLETE'
    assert analyze_number('1004',P,'1001')=='LOCAL'
    assert analyze_number('10022',P,'1001')=='INVALID'
    assert analyze_number('１００２',P,'1001')=='INVALID'  # 全角数字不是合法拨号字符

def test_hook_events_sorted_both_directions():
    prev={'1002':0,'1001':1}
    cur={'1002':1,'1001':0}
    assert detect_hook_events(prev,cur)==[{'user':'1001','kind':'ONHOOK'},{'user':'1002','kind':'OFFHOOK'}]

def test_waiting_user_is_busy():
    s=connected()
    s.enqueue(1000,'ONHOOK','1001')  # 主叫挂机；1002 仍摘机，进入 WAIT_ONHOOK
    dial(s,'1003','1002',1100)       # 1002 尚未真正挂机时尝试呼叫它
    s.run()
    assert s.calls['C1'].reason=='NORMAL_CLEAR'
    assert s.calls['C2'].reason=='USER_BUSY'   # 1002 在等待挂机集合，不可被叫
    assert '1002' in s.waiting and not s.tables.pairs
