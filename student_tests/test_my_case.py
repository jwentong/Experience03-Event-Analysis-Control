from src.runtime import Exchange
from src.scenarios import dial


def test_invalid_call_waits_for_real_onhook_before_reuse():
    """非法呼叫结束后，主叫必须真实挂机，才能重新发起呼叫。"""

    s = Exchange()

    # 1001拨打非法号码，呼叫结束，但1001仍处于摘机状态
    dial(s, number="9999")
    s.run(500)

    assert s.calls["C1"].state == "ENDED"
    assert s.calls["C1"].reason == "INVALID"
    assert "1001" in s.waiting
    assert "1001" not in s.owners

    # 再次发送摘机事件，由于用户没有真实挂机，不应创建新呼叫
    s.enqueue(600, "OFFHOOK", "1001")
    s.run(600)

    assert len(s.calls) == 1
    assert "1001" in s.waiting

    # 用户真实挂机后，再次摘机应能够创建新呼叫
    s.enqueue(700, "ONHOOK", "1001")
    s.enqueue(800, "OFFHOOK", "1001")
    s.run(800)

    assert "1001" not in s.waiting
    assert len(s.calls) == 2
    assert s.calls["C2"].caller == "1001"
    assert s.calls["C2"].state == "COLLECTING"