from src.runtime import Exchange
from src.scenarios import dial


def test_partial_digits_do_not_extend_dial_deadline():
    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1001")
    exchange.enqueue(4900, "DIGIT", "1001", "1")
    exchange.enqueue(4999, "DIGIT", "1001", "0")
    exchange.run(4999)
    call = exchange.calls["C1"]
    assert (call.state, call.digits) == ("COLLECTING", "10")

    exchange.run(5000)
    assert (call.state, call.reason) == ("ENDED", "DIAL_TIMEOUT")
    assert exchange.waiting == {"1001"}
    assert not exchange.owners and not exchange.tables.pairs

    exchange.enqueue(5100, "ONHOOK", "1001")
    dial(exchange, start=5200)
    exchange.enqueue(6000, "OFFHOOK", "1002")
    exchange.run()
    assert exchange.calls["C2"].state == "CONNECTED"
    assert set(exchange.tables.pairs) == {"C2"}
