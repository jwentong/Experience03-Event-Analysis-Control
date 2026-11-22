"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

DIGITS='0123456789'

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if len(digits)>4 or any(ch not in DIGITS for ch in digits):
        return 'INVALID'
    if digits in dial_plan:
        return 'SELF_CALL' if digits==caller else 'LOCAL'
    if any(number.startswith(digits) for number in dial_plan):
        return 'INCOMPLETE'
    return 'INVALID'
