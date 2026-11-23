"""号码分析与拨号计划匹配。"""


def analyze_number(digits, dial_plan, caller):
    """按四位拨号计划判定号码是前缀、本地号、自呼或非法号码。"""
    if not isinstance(digits, str) or len(digits) > 4:
        return "INVALID"
    if any(char < "0" or char > "9" for char in digits):
        return "INVALID"

    valid_numbers = [
        number
        for number in dial_plan
        if isinstance(number, str)
        and len(number) == 4
        and all("0" <= char <= "9" for char in number)
    ]
    if not any(number.startswith(digits) for number in valid_numbers):
        return "INVALID"
    if len(digits) < 4:
        return "INCOMPLETE"
    if digits == caller:
        return "SELF_CALL"
    return "LOCAL"
