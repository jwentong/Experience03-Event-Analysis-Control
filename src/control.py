"""Call control state transitions used by the exchange runtime."""

from src.numbering import analyze_number


def handle_call_event(c, e, s, actions):
    """Apply a non-timeout event to a Call and record user-facing actions."""
    if c.state == 'ENDED':
        return

    kind = e.get('kind')
    if kind == 'ONHOOK':
        reason = 'NORMAL_CLEAR' if c.state == 'CONNECTED' else 'CALLER_CANCEL'
        s.finish(c, reason)
        s.action(actions, 'RELEASE')
        return

    if c.state == 'COLLECTING':
        if kind == 'OFFHOOK' and e.get('user') == c.caller:
            s.action(actions, 'DIAL_TONE')
            s.arm(c, 'DIAL', 5000)
            return
        if kind != 'DIGIT' or e.get('user') != c.caller:
            return
        value = e.get('value')
        c.digits += value if isinstance(value, str) else str(value)
        s.action(actions, 'STOP_DIAL_TONE')
        result = analyze_number(c.digits, s.numbers, c.caller)
        if result == 'INCOMPLETE':
            return
        if result in ('INVALID', 'SELF_CALL'):
            s.finish(c, result)
            s.action(actions, 'FAIL_TONE', reason=result)
            return
        if not s.reserve(c, c.digits):
            s.finish(c, 'USER_BUSY')
            s.action(actions, 'BUSY_TONE')
            return
        s.cancel(c)
        c.state = 'RINGING'
        s.arm(c, 'RING', 10000)
        s.action(actions, 'RING', user=c.callee)
        s.action(actions, 'RINGBACK', user=c.caller)
        return

    if c.state == 'RINGING' and kind == 'OFFHOOK' and e.get('user') == c.callee:
        s.cancel(c)
        if s.activate(c):
            c.state = 'CONNECTED'
            s.action(actions, 'STOP_RING')
            s.action(actions, 'CONNECT')
        else:
            s.finish(c, 'NETWORK_BUSY')
            s.action(actions, 'FAIL_TONE', reason='NETWORK_BUSY')
