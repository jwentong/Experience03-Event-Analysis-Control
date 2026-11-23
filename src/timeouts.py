"""Timer event handling for dialing and ringing states."""


def handle_timeout(c, e, s, actions):
    """Ignore stale timers and finish only the currently active timer state."""
    if c.state == 'ENDED':
        return
    if e.get('token') != c.timer or e.get('value') != c.timer_kind:
        return
    if c.state == 'COLLECTING' and e.get('value') == 'DIAL':
        s.finish(c, 'DIAL_TIMEOUT')
        s.action(actions, 'FAIL_TONE', reason='DIAL_TIMEOUT')
    elif c.state == 'RINGING' and e.get('value') == 'RING':
        s.finish(c, 'NO_ANSWER')
        s.action(actions, 'STOP_RING')
        s.action(actions, 'FAIL_TONE', reason='NO_ANSWER')
