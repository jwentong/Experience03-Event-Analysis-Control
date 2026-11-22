from src.runtime import Exchange


def test_call_to_configured_user_connects_both_timeslot_directions():
    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1003")
    for time_ms, digit in enumerate("1004", start=1):
        exchange.enqueue(time_ms, "DIGIT", "1003", digit)
    exchange.enqueue(10, "OFFHOOK", "1004")
    exchange.run()

    assert exchange.calls["C1"].state == "CONNECTED"
    assert exchange.tables.t_maps[0] == {4: 3, 3: 4}
