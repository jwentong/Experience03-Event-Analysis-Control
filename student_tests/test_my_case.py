from src.runtime import Exchange
from src.scenarios import dial


def test_stale_dial_timeout_does_not_end_ringing_call():
    exchange = Exchange()
    dial(exchange)
    exchange.run(500)

    call = exchange.calls["C1"]
    assert call.state == "RINGING"
    exchange.enqueue(
        600,
        "TIMEOUT",
        value="DIAL",
        call_id=call.call_id,
        token=1,
    )
    exchange.run(600)

    assert call.state == "RINGING"
    assert call.timer_kind == "RING"
    assert exchange.owners["1002"] == call.call_id