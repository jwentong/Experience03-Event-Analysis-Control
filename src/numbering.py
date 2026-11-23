"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if len(digits)>4 or (digits and not digits.isdigit()):return 'INVALID'
    if digits=='' :return 'INCOMPLETE' if dial_plan else 'INVALID'
    if len(digits)==4:
        if digits==caller:return 'SELF_CALL'
        if digits in dial_plan:return 'LOCAL'
        return 'INVALID'
    return 'INCOMPLETE' if any(n.startswith(digits) for n in dial_plan) else 'INVALID'
