"""Dial-plan number analysis."""


def analyze_number(digits, dial_plan, caller):
    """Classify a four-digit dial string as incomplete, local, self, or invalid."""
    if not isinstance(digits, str):
        return "INVALID"
    numbers = [number for number in dial_plan
               if isinstance(number, str) and len(number) == 4 and number.isdigit()]
    if len(digits) > 4 or (digits and not digits.isdigit()):
        return "INVALID"
    if not any(number.startswith(digits) for number in numbers):
        return "INVALID"
    if len(digits) < 4:
        return "INCOMPLETE"
    if digits == caller:
        return "SELF_CALL"
    return "LOCAL" if digits in numbers else "INVALID"
