"""自拟测试：验证重复摘机采样不创建重复呼叫。"""
from src.runtime import Exchange


def test_duplicate_offhook_does_not_create_second_call():
    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1001")
    exchange.enqueue(1, "OFFHOOK", "1001")
    exchange.run(2)

    assert len(exchange.calls) == 1
    assert exchange.calls["C1"].state == "COLLECTING"
