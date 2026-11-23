"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits, str) or len(digits) > 4 or any(char not in "0123456789" for char in digits):
        return "INVALID"

    valid_numbers = {
        number for number in dial_plan
        if isinstance(number, str) and len(number) == 4 and all(char in "0123456789" for char in number)
    }
    matches = {number for number in valid_numbers if number.startswith(digits)}
    if not matches:
        return "INVALID"
    if len(digits) < 4:
        return "INCOMPLETE"
    if digits == caller:
        return "SELF_CALL"
    return "LOCAL" if digits in valid_numbers else "INVALID"
