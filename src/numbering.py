"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > 4:
        return "INVALID"
    if digits == "":
        plan = list(dial_plan) if dial_plan is not None else []
        return "INCOMPLETE" if any(isinstance(number, str) and number.startswith("") for number in plan) else "INVALID"
    if not digits.isdigit():
        return "INVALID"

    plan = list(dial_plan) if dial_plan is not None else []
    if not all(isinstance(number, str) for number in plan):
        return "INVALID"

    if not any(number.startswith(digits) for number in plan):
        return "INVALID"
    if not any(number == digits for number in plan):
        return "INCOMPLETE"
    if digits == caller:
        return "SELF_CALL"
    return "LOCAL"
