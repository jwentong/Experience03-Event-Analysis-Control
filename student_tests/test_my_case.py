from src.runtime import Exchange


def test_partial_digits_do_not_extend_dial_timeout():
    """输入数字不重置摘机时启动的5000ms总收号超时。"""
    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1001")
    exchange.enqueue(1000, "DIGIT", "1001", "1")
    exchange.enqueue(2000, "DIGIT", "1001", "0")
    exchange.run()

    call = exchange.calls["C1"]
    assert call.state == "ENDED"
    assert call.reason == "DIAL_TIMEOUT"
    assert call.digits == "10"
    assert not exchange.tables.pairs
