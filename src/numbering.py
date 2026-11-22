"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > 4:
        return 'INVALID'
    if any(ch < '0' or ch > '9' for ch in digits):
        return 'INVALID'

    numbers = tuple(dial_plan)
    if len(digits) < 4:
        return 'INCOMPLETE' if any(str(number).startswith(digits) for number in numbers) else 'INVALID'

    if digits not in {str(number) for number in numbers}:
        return 'INVALID'
    return 'SELF_CALL' if digits == caller else 'LOCAL'
