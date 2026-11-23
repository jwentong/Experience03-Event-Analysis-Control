from src.runtime import Exchange
from src.scenarios import dial
from src.switch_engine import run_frames, sample_frame


def test_releasing_one_call_preserves_the_other_after_stale_timeouts():
    exchange = Exchange()
    dial(exchange, caller="1001", number="1002")
    dial(exchange, caller="1003", number="1004")
    exchange.enqueue(800, "OFFHOOK", "1002")
    exchange.enqueue(900, "OFFHOOK", "1004")
    exchange.enqueue(1000, "ONHOOK", "1001")

    exchange.run(900)
    assert {call.state for call in exchange.calls.values()} == {"CONNECTED"}
    assert set(exchange.tables.pairs) == {"C1", "C2"}
    frame = sample_frame(0)
    before = run_frames([frame], exchange.tables)[0]
    assert (before["input_frame_id"], before["available_frame_id"]) == (0, 1)
    assert before["output"][0, 1:5].tolist() == [6, 3, 12, 9]

    exchange.run()
    assert exchange.calls["C1"].reason == "NORMAL_CLEAR"
    assert exchange.calls["C2"].state == "CONNECTED"
    assert exchange.waiting == {"1002"}
    assert exchange.owners == {"1003": "C2", "1004": "C2"}
    assert set(exchange.tables.pairs) == {"C2"}
    after = run_frames([frame], exchange.tables)[0]
    assert after["output"][0, 1:5].tolist() == [0xD5, 0xD5, 12, 9]

    expired = [row for row in exchange.logs if row["event"]["kind"] == "TIMEOUT"]
    assert [(row["time_ms"], row["call_id"]) for row in expired] == [
        (5000, "C1"),
        (5000, "C2"),
        (10400, "C1"),
        (10400, "C2"),
    ]
    assert all(row["before"] == row["after"] and not row["actions"] for row in expired)
