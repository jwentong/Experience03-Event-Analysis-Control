"""号码分析：判断当前已收数字是继续收号、完整号码、自呼还是非法。"""

DIGITS = "0123456789"
MAX_LENGTH = 4


def analyze_number(digits, dial_plan, caller):
    # 只允许数字；空串表示"还没输入"，不在这里判错
    if any(ch not in DIGITS for ch in digits):
        return "INVALID"

    # 四位号码，超长直接判错，不能因为前四位能匹配就放过
    if len(digits) > MAX_LENGTH:
        return "INVALID"

    # 已经是一个完整合法的号码
    if digits in dial_plan:
        return "SELF_CALL" if digits == caller else "LOCAL"

    # 仍然是某个合法号码的前缀，继续收号
    if any(number.startswith(digits) for number in dial_plan):
        return "INCOMPLETE"

    # 既不是完整号，也不是任何号码的前缀
    return "INVALID"
