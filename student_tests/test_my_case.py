from src.hooks import detect_hook_events
from src.numbering import analyze_number

def test_my_custom_logic():
    # 测试摘挂机检测
    events = detect_hook_events({"1001": 0, "1002": 0}, {"1001": 1, "1002": 0})
    assert len(events) == 1
    assert events[0]["user"] == "1001"
    assert events[0]["kind"] == "OFFHOOK"

    # 测试号码分析
    plan = ["1001", "1002", "1003", "1004"]
    assert analyze_number("100", plan, "1001") == "INCOMPLETE"
    assert analyze_number("1002", plan, "1001") == "LOCAL"
    assert analyze_number("1001", plan, "1001") == "SELF_CALL"
    assert analyze_number("9999", plan, "1001") == "INVALID"