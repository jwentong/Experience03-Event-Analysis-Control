"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

NUMBER_LENGTH = 4


def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > NUMBER_LENGTH:
        return 'INVALID'
    if digits and not digits.isdigit():
        return 'INVALID'
    plan = [str(number) for number in dial_plan]
    for number in plan:
        if number == digits:
            return 'SELF_CALL' if digits == caller else 'LOCAL'
    if any(number.startswith(digits) for number in plan):
        return 'INCOMPLETE'
    return 'INVALID'
