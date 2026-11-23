"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits, dial_plan, caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > 4 or any(ch not in '0123456789' for ch in digits):
        return 'INVALID'
    if digits == caller:
        return 'SELF_CALL'
    if digits in dial_plan:
        return 'LOCAL' if len(digits) == 4 else 'INVALID'
    if any(p.startswith(digits) for p in dial_plan):
        return 'INCOMPLETE'
    return 'INVALID'
