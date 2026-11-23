from src.runtime import Exchange
from src.scenarios import dial
from src.switch_engine import run_frames, sample_frame


def test_wrong_timer_kind_preserves_ringing_and_answer_builds_route():
    exchange = Exchange()
    dial(exchange)
    exchange.run(400)
    call = exchange.calls["C1"]

    # A matching token cannot make a DIAL event valid during ringing.
    exchange.enqueue(450, "TIMEOUT", value="DIAL", call_id=call.call_id, token=call.timer)
    exchange.run(450)
    assert call.state == "RINGING"
    assert exchange.logs[-1]["actions"] == []
    assert exchange.owners == {"1001": "C1", "1002": "C1"}
    assert exchange.tables.pairs == {}

    frame = sample_frame(0)
    exchange.enqueue(800, "OFFHOOK", "1002")
    exchange.run(800)
    assert call.state == "CONNECTED"
    result, = run_frames([frame], exchange.tables)
    assert (result["input_frame_id"], result["available_frame_id"]) == (0, 1)
    assert list(result["output"][0, 1:3]) == [6, 3]

    exchange.enqueue(1000, "ONHOOK", "1001")
    exchange.run()
    assert call.reason == "NORMAL_CLEAR"
    assert exchange.waiting == {"1002"}
    assert not exchange.owners and not exchange.tables.pairs
    result, = run_frames([frame], exchange.tables)
    assert list(result["output"][0, 1:3]) == [0xD5, 0xD5]
