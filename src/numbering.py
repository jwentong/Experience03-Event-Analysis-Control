"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits, dial_plan, caller):
    if not all(ch in "0123456789" for ch in digits):
        return "INVALID"
    digit_len = len(digits)
    if digit_len > 4:
        return "INVALID"
    if digit_len == 4:
        if digits not in dial_plan:
            return "INVALID"
        if digits == caller:
            return "SELF_CALL"
        else:
            return "LOCAL"
    else:
        is_prefix = any(num.startswith(digits) for num in dial_plan)
        if is_prefix:
            return "INCOMPLETE"
        else:
            return "INVALID"

