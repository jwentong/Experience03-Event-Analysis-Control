"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str):
        return "INVALID"
    if len(digits) > 4 or any(ch < "0" or ch > "9" for ch in digits):
        return "INVALID"

    configured = set(dial_plan)
    if len(digits) == 4:
        if digits not in configured:
            return "INVALID"
        return "SELF_CALL" if digits == caller else "LOCAL"

    if any(number.startswith(digits) for number in configured):
        return "INCOMPLETE"
    return "INVALID"
