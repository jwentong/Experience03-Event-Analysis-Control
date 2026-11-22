"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

VALID_DIGITS = set('0123456789')


def analyze_number(digits, dial_plan, caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str):
        return 'INVALID'
    if any(ch not in VALID_DIGITS for ch in digits):
        return 'INVALID'
    if len(digits) > 4:
        return 'INVALID'

    # 空串也是所有号码的前缀，表示刚开始收号
    candidates = [number for number in dial_plan if number.startswith(digits)]
    if not candidates:
        return 'INVALID'

    if len(digits) < 4:
        return 'INCOMPLETE'

    # 四位且能在号码表里找到，才可能是本局号码
    if digits not in dial_plan:
        return 'INVALID'
    if digits == caller:
        return 'SELF_CALL'
    return 'LOCAL'
