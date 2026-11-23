"""用户号码分析。"""


def analyze_number(digits, dial_plan, caller):
    """分析已输入号码，返回对应的号码分析结果。"""

    # 输入必须是字符串，并且只能包含ASCII数字
    if not isinstance(digits, str):
        return "INVALID"

    if any(char not in "0123456789" for char in digits):
        return "INVALID"

    # 本实验使用四位号码
    if len(digits) > 4:
        return "INVALID"

    # 只保留号码表中的合法四位号码
    valid_numbers = {
        number
        for number in dial_plan
        if isinstance(number, str)
        and len(number) == 4
        and all(char in "0123456789" for char in number)
    }

    # 输入四位后必须与号码表中的某个号码完全匹配
    if len(digits) == 4:
        if digits not in valid_numbers:
            return "INVALID"

        if digits == caller:
            return "SELF_CALL"

        return "LOCAL"

    # 未输入满四位，但仍是某个合法号码的前缀
    if any(number.startswith(digits) for number in valid_numbers):
        return "INCOMPLETE"

    return "INVALID"