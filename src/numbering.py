"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

LENGTH=4
DIGITS=set('0123456789')

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if not isinstance(digits,str):
        return 'INVALID'
    # 先判字符集：非十进制字符不可能构成号码，先排除避免被前缀比较掩盖。
    if any(ch not in DIGITS for ch in digits):
        return 'INVALID'
    # 本实验号码固定四位，超长直接判错，不进入前缀比较。
    if len(digits)>LENGTH:
        return 'INVALID'
    plan=[str(number) for number in (dial_plan or [])]
    # 收号中途只有仍是某个合法号码的前缀才继续，否则立即判错。
    if not any(number.startswith(digits) for number in plan):
        return 'INVALID'
    if len(digits)<LENGTH:
        return 'INCOMPLETE'
    if digits==str(caller):
        return 'SELF_CALL'
    return 'LOCAL' if digits in plan else 'INVALID'
