"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits: str, dial_plan, caller: str) -> str:
    # 空字符串是任何号码的前缀，视为未收完
    if digits == "":
        return "INCOMPLETE"

    # 非法字符（只允许数字）
    if not digits.isdigit():
        return "INVALID"

    # 过长
    if len(digits) > 4:
        return "INVALID"

    # 兼容 dial_plan 是 list 或 dict 两种情况
    if isinstance(dial_plan, dict):
        plan = [str(k) for k in dial_plan.keys()]
    else:
        plan = [str(x) for x in dial_plan]

    # 未满四位：判断是否存在以当前 digits 为前缀的合法号
    if len(digits) < 4:
        if any(num.startswith(digits) for num in plan):
            return "INCOMPLETE"
        return "INVALID"

    # 满四位：必须是合法号
    if digits not in plan:
        return "INVALID"

    # 自呼
    if digits == str(caller):
        return "SELF_CALL"

    return "LOCAL"
