"""Analyze four-digit numbers against the configured dial plan."""


def analyze_number(digits, dial_plan, caller):
    """Classify a complete number or a valid prefix."""
    if not isinstance(digits, str) or len(digits) > 4:
        return "INVALID"
    if any(digit not in "0123456789" for digit in digits):
        return "INVALID"
    if len(digits) < 4:
        if any(number.startswith(digits) for number in dial_plan):
            return "INCOMPLETE"
        return "INVALID"
    if digits not in dial_plan:
        return "INVALID"
    return "SELF_CALL" if digits == caller else "LOCAL"
