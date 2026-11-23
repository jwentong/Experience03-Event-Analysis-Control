"""自拟反例：收号中途挂机后，旧收号超时不得改写结束状态。"""

from src.runtime import Exchange


def test_cancel_during_collection_ignores_stale_dial_timeout():
    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1001")
    exchange.enqueue(100, "DIGIT", "1001", "1")
    exchange.enqueue(200, "ONHOOK", "1001")
    exchange.run()

    call = exchange.calls["C1"]
    assert call.state == "ENDED"
    assert call.reason == "CALLER_CANCEL"
    assert not exchange.owners
    assert not exchange.tables.pairs
    assert "1001" not in exchange.waiting

    stale_event = next(
        row for row in exchange.logs
        if row["event"]["kind"] == "TIMEOUT"
        and row["event"]["value"] == "DIAL"
    )
    assert stale_event["before"] == stale_event["after"] == "ENDED"
    assert stale_event["actions"] == []
    assert stale_event["reason"] == "CALLER_CANCEL"
