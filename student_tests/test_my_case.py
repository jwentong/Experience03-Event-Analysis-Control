"""自拟测试：补测公开测试没有覆盖到的边界。"""
from src.hooks import detect_hook_events
from src.numbering import analyze_number
from src.runtime import Exchange
from src.scenarios import dial


def test_hook_edges_sorted_and_pure():
    """四个用户同时跳变时按编号排序返回，且不修改调用方传入的采样。"""
    previous = {"1004": 1, "1003": 0, "1002": 1, "1001": 0}
    current = {"1004": 0, "1003": 1, "1002": 1, "1001": 1}
    assert detect_hook_events(previous, current) == [
        {"user": "1001", "kind": "OFFHOOK"},
        {"user": "1003", "kind": "OFFHOOK"},
        {"user": "1004", "kind": "ONHOOK"},
    ]
    assert previous["1004"] == 1


def test_callee_offhook_before_dial_is_busy():
    """被叫先摘机、尚未占位时，主叫拨它应当得到 USER_BUSY，且不影响原有呼叫。"""
    s = Exchange()
    s.enqueue(0, "OFFHOOK", "1003")
    dial(s, "1001", "1003", 100)
    s.run(600)
    assert s.calls["C2"].reason == "USER_BUSY"
    assert s.calls["C1"].state == "COLLECTING"
    assert not s.tables.pairs


def test_numbering_follows_dial_plan():
    """号码分析必须由 dial_plan 驱动，而不是写死 1001~1004。"""
    plan = ["2001", "2002", "2003"]
    assert analyze_number("2002", plan, "2001") == "LOCAL"
    assert analyze_number("2003", plan, "2003") == "SELF_CALL"
    assert analyze_number("2", plan, "2001") == "INCOMPLETE"
    assert analyze_number("2009", plan, "2001") == "INVALID"
