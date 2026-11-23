# student_tests/test_my_case.py
"""
实验三 自拟测试用例
满足要求：位于student_tests，test_开头函数，调用实验任务函数，带有assert断言
不依赖Runtime高层仿真，直接对学生实现的4个底层函数做单元测试
"""
from src.hooks import detect_hook_events
from src.numbering import analyze_number


def test_detect_hook_basic_transition():
    """测试摘挂机状态跃迁事件生成"""
    prev = {1001: 0, 1002: 1, 1003: 0}
    curr = {1001: 1, 1002: 0, 1003: 0}
    events = detect_hook_events(prev, curr)
    assert len(events) == 2
    assert events[0]["user"] == 1001 and events[0]["kind"] == "OFFHOOK"
    assert events[1]["user"] == 1002 and events[1]["kind"] == "ONHOOK"


def test_detect_hook_no_change():
    """用户状态全部不变，返回空事件列表"""
    prev = {1001: 0, 1002: 1}
    curr = {1001: 0, 1002: 1}
    events = detect_hook_events(prev, curr)
    assert events == []


def test_analyze_incomplete_prefix():
    """号码前缀匹配，返回INCOMPLETE"""
    dial_plan = {"1001", "1002", "1003", "1004"}
    res = analyze_number("10", dial_plan, "1001")
    assert res == "INCOMPLETE"


def test_analyze_self_call():
    """呼叫自己号码返回SELF_CALL"""
    dial_plan = {"1001", "1002"}
    res = analyze_number("1001", dial_plan, "1001")
    assert res == "SELF_CALL"


def test_analyze_local_valid():
    """合法外部本地号码返回LOCAL"""
    dial_plan = {"1001", "1002"}
    res = analyze_number("1002", dial_plan, "1001")
    assert res == "LOCAL"


def test_analyze_invalid_char():
    """包含非法字符返回INVALID"""
    dial_plan = {"1001", "1002"}
    res = analyze_number("10a1", dial_plan, "1001")
    assert res == "INVALID"


def test_analyze_too_long():
    """号码超过四位返回INVALID"""
    dial_plan = {"1001", "1002"}
    res = analyze_number("10015", dial_plan, "1001")
    assert res == "INVALID"
