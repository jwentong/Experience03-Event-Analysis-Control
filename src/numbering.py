"""Analyze collected digits against the configured four-digit dial plan."""


def analyze_number(digits, dial_plan, caller):
    """Classify a partial, local, self-call, or invalid number."""
    if not isinstance(digits, str) or len(digits) > 4:
        return "INVALID"
    if any(character < "0" or character > "9" for character in digits):
        return "INVALID"

    numbers = [
        number for number in dial_plan
        if isinstance(number, str)
        and len(number) == 4
        and all("0" <= character <= "9" for character in number)
    ]
    if len(digits) < 4:
        return "INCOMPLETE" if any(number.startswith(digits) for number in numbers) else "INVALID"
    if digits not in numbers:
        return "INVALID"
    return "SELF_CALL" if digits == caller else "LOCAL"
