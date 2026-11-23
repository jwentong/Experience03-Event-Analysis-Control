from src.numbering import analyze_number
from src.runtime import Exchange


def test_number_analysis_and_real_call_setup():
    plan = ["1001", "1002", "1003", "1004"]
    assert analyze_number("100", plan, "1001") == "INCOMPLETE"
    assert analyze_number("1001", plan, "1001") == "SELF_CALL"

    exchange = Exchange()
    exchange.enqueue(0, "OFFHOOK", "1001")
    exchange.run(0)
    assert exchange.calls["C1"].state == "COLLECTING"
