from src.hooks import detect_hook_events
from src.numbering import analyze_number
from src.runtime import Exchange


def test_hook_events_only_changes():
    """相同采样不产生事件，只有变化的用户产生事件，且按号码排序。"""
    prev = {1001: 0, 1002: 0, 1003: 1}
    curr = {1001: 1, 1002: 0, 1003: 1}
    events = detect_hook_events(prev, curr)
    assert events == [{"kind": "OFFHOOK", "user": 1001}]


def test_hook_events_reject_bad_value():
    """采样值不是 0/1 时必须抛 ValueError。"""
    prev = {1001: 0}
    curr = {1001: 2}
    raised = False
    try:
        detect_hook_events(prev, curr)
    except ValueError:
        raised = True
    assert raised


def test_numbering_basic():
    """覆盖 INCOMPLETE / LOCAL / SELF_CALL / INVALID 四类结果。"""
    plan = ["1001", "1002", "1003", "1004"]
    assert analyze_number("", plan, "1001") == "INCOMPLETE"
    assert analyze_number("100", plan, "1001") == "INCOMPLETE"
    assert analyze_number("1002", plan, "1001") == "LOCAL"
    assert analyze_number("1001", plan, "1001") == "SELF_CALL"
    assert analyze_number("9", plan, "1001") == "INVALID"
    assert analyze_number("10022", plan, "1001") == "INVALID"
    assert analyze_number("a", plan, "1001") == "INVALID"


def test_exchange_offhook_gives_dial_tone():
    """主叫摘机后框架创建 Call，并进入 COLLECTING，首个动作是 DIAL_TONE。"""
    s = Exchange()
    s.enqueue(0, "OFFHOOK", "1001")
    s.run(0)
    assert s.calls["C1"].state == "COLLECTING"
    assert s.logs[0]["actions"][0]["type"] == "DIAL_TONE"