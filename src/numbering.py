"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""


def analyze_number(digits, dial_plan, caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or not all(ch in '0123456789' for ch in digits):
        return 'INVALID'
    if len(digits) > 4:
        return 'INVALID'

    plan = {str(number) for number in dial_plan}
    if len(digits) < 4:
        return 'INCOMPLETE' if any(number.startswith(digits) for number in plan) else 'INVALID'

    if digits not in plan:
        return 'INVALID'
    if digits == str(caller):
        return 'SELF_CALL'
    return 'LOCAL'
