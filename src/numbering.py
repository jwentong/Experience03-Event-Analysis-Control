"""学生任务：四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""

def analyze_number(digits, dial_plan, caller):
    """四位号码；合法前缀返回INCOMPLETE，完整合法号LOCAL，自己的号SELF_CALL；非法字符、无匹配前缀、超过四位INVALID。"""
    
    # 1. 非法字符检查（允许空字符串，空字符串表示还没开始拨号）
    if digits and not digits.isdigit():
        return "INVALID"
        
    # 2. 超过四位检查
    if len(digits) > 4:
        return "INVALID"
        
    # 3. 无匹配前缀检查
    has_prefix = False
    for num in dial_plan:
        if num.startswith(digits):
            has_prefix = True
            break
            
    if not has_prefix:
        return "INVALID"
        
    # 4. 长度不足4位，且前缀匹配
    if len(digits) < 4:
        return "INCOMPLETE"
        
    # 5. 长度刚好4位且合法
    if digits == caller:
        return "SELF_CALL"
    else:
        return "LOCAL"