"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

_NUMBER_LENGTH=4
_DIGITS='0123456789'

def analyze_number(digits,dial_plan,caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    if isinstance(digits,str) and digits=='':
        return 'INCOMPLETE'  # 还没有输入任何数字，继续收号
    if not isinstance(digits,str) or any(ch not in _DIGITS for ch in digits):
        return 'INVALID'  # 含非 0-9 字符
    if len(digits)>_NUMBER_LENGTH:
        return 'INVALID'  # 超过四位，不可能再成为合法号码
    if digits==caller:
        return 'SELF_CALL'  # 自己的号码优先于普通本局号码
    if digits in dial_plan:
        return 'LOCAL'  # 拨号计划中的完整合法号码
    if any(isinstance(number,str) and number.startswith(digits) for number in dial_plan):
        return 'INCOMPLETE'  # 仍是某个合法号码的前缀，等待后续按键
    return 'INVALID'  # 没有任何合法号码以它开头
