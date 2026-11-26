"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
"""四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
def analyze_number(digits: str, dial_plan: set[str], caller: int) -> str:
    
    # 空字符串特殊放行，空串是合法前缀
    if len(digits) > 0 and not digits.isdigit():
        return "INVALID"

    if len(digits) > 4:
        return "INVALID"

    caller_str = str(caller)
    is_prefix = any(num.startswith(digits) for num in dial_plan)

    if len(digits) < 4:
        if is_prefix:
            return "INCOMPLETE"
        else:
            return "INVALID"

    # 到这里 len(digits)==4
    if digits not in dial_plan:
        return "INVALID"

    if digits == caller_str:
        return "SELF_CALL"
    else:
        return "LOCAL"


