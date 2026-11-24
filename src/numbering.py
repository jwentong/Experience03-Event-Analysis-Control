"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits, dial_plan, caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    # 过长
    if len(digits) > 4:
        return 'INVALID'
    
    # 空字符串处理
    if digits == '':
        return 'INCOMPLETE' if any(num.startswith('') for num in dial_plan) else 'INVALID'
        
    # 非法字符
    if not digits.isdigit():
        return 'INVALID'
    
    # 检查是否有任何号码以 digits 开头
    is_prefix = any(num.startswith(digits) for num in dial_plan)
    if not is_prefix:
        return 'INVALID'
    
    # 检查是否为完整号码
    if len(digits) == 4:
        if digits in dial_plan:
            if digits == caller:
                return 'SELF_CALL'
            return 'LOCAL'
        return 'INVALID'
    else:
        return 'INCOMPLETE'