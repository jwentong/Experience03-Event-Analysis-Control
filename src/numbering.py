"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > 4:
        return "INVALID"
    if any(digit not in "0123456789" for digit in digits):
        return "INVALID"
    if len(digits) < 4:
        return "INCOMPLETE" if any(number.startswith(digits) for number in dial_plan) else "INVALID"
    if digits not in dial_plan:
        return "INVALID"
    return "SELF_CALL" if digits == caller else "LOCAL"
