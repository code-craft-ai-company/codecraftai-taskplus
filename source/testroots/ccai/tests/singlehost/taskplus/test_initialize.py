"""
    Tests for :func:`ccai.taskplus.initialize.initialize_taskplus_runtime`.

    The persona establishment and runtime variable resolution are patched so the
    tests verify how the TaskPlus runtime is initialized without changing the
    runtime of the process that is running the tests.
"""

import os

from unittest import mock

from ccai.testbase import verification

from ccai.taskplus import initialize


def test_initialize_establishes_persona_then_resolves_runtime_variables() -> None:
    """
        The runtime initialization establishes the 'ccai' persona, sharing the '~/ccai'
        presence directory with the other ccai commands, and then resolves the runtime
        variables.
    """

    manager = mock.MagicMock()

    with mock.patch.object(initialize, "establish_app_persona") as mock_establish, \
         mock.patch.object(initialize, "resolve_runtime_variables") as mock_resolve:

        manager.attach_mock(mock_establish, "establish_app_persona")
        manager.attach_mock(mock_resolve, "resolve_runtime_variables")

        initialize.initialize_taskplus_runtime()

    expected_home_dir = os.path.join(os.path.expanduser("~"), "ccai")

    expected_calls = [
        mock.call.establish_app_persona(name="ccai", presence_dir=expected_home_dir, logger_name="TaskPlus",
                                        log_basename="workflow"),
        mock.call.resolve_runtime_variables(),
    ]
    verification.assert_equal(manager.mock_calls, expected_calls)
    return
