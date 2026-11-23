"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not digits:
        return 'INCOMPLETE'
    if not all(ch in '0123456789' for ch in digits):
        return 'INVALID'
    if len(digits)>4:
        return 'INVALID'
    if not any(number.startswith(digits) for number in dial_plan):
        return 'INVALID'
    if len(digits)<4:
        return 'INCOMPLETE'
    if digits==caller:
        return 'SELF_CALL'
    return 'LOCAL'
