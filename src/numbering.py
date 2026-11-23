"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str):
        return "INVALID"
    for ch in digits:
        if ch not in "0123456789":
            return "INVALID"

    if digits in dial_plan:
        return "SELF_CALL" if digits == caller else "LOCAL"

    if len(digits) >= 4:
        return "INVALID"

    for num in dial_plan:
        if num.startswith(digits):
            return "INCOMPLETE"

    return "INVALID"
