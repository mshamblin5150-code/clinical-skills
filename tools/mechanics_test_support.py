"""Pin older row fixtures immediately before the new mechanics contract.

Those fixtures test earlier grader rows, including frozen historical controls.
test_coursework_mechanics separately exercises the current public commands.
"""

from datetime import timedelta
from unittest import mock

import completion_checks

_active = completion_checks.active


def begin():
    cutoff, _ = completion_checks.registry()["coursework_mechanics:mechanics-language"]
    def historical(key, *args, **kwargs):
        if key.startswith("coursework_mechanics:"):
            return _active(key, cutoff - timedelta(seconds=1))
        return _active(key, *args, **kwargs)
    patch = mock.patch.object(completion_checks, "active", side_effect=historical)
    patch.start()
    return patch


def end(token):
    token.stop()


def module_hooks():
    scopes = []

    def setup():
        scopes.append(begin())

    def teardown():
        end(scopes.pop())

    return setup, teardown
