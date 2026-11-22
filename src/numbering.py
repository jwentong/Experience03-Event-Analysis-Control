"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    # 采用ASCII数字，避免把全角数字等字符识别为合法拨号。
    if (not isinstance(digits, str) or len(digits) > 4
            or any(ch not in '0123456789' for ch in digits)):
        return 'INVALID'
    numbers = [n for n in dial_plan if isinstance(n, str)
               and len(n) == 4 and all(ch in '0123456789' for ch in n)]
    if not any(n.startswith(digits) for n in numbers):
        return 'INVALID'
    if len(digits) < 4:
        return 'INCOMPLETE'
    return 'SELF_CALL' if digits == caller else 'LOCAL'
