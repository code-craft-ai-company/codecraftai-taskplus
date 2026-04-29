"""
    Tests for the legacy function-based execution module
    :mod:`automojo.taskplus.execution`.

    Failure-handling jump paths (``onfailure`` / ``onsuccess``) that require
    a task which returns a non-zero exit code are exercised by the
    :class:`FlowEngine` tests instead, since the published task classes only
    return ``0`` and writing a synthetic task module from a test would be
    brittle.
"""

import logging
import os

from automojo.testbase import verification

from automojo.errors.exceptions import ConfigurationError

from automojo.taskplus.execution import (
    JumpContext,
    execute_tasklist,
    execute_workflow,
)


_GIT_TASKTYPE = "automojo.taskplus.tasks.gitcheckout@GitCheckout"
_LOGGER = logging.getLogger("automojo.tests.singlehost.taskplus.test_execution")


# ---------------------------------------------------------------------------
# JumpContext
# ---------------------------------------------------------------------------


def test_jumpcontext_initial_on_failure_section_is_none() -> None:
    """A freshly constructed JumpContext has ``on_failure_section`` of ``None``."""

    ctx = JumpContext()

    on_failure_value = ctx.on_failure_section

    verification.assert_true(on_failure_value is None)
    return


def test_jumpcontext_initial_on_success_section_is_none() -> None:
    """A freshly constructed JumpContext has ``on_success_section`` of ``None``."""

    ctx = JumpContext()

    on_success_value = ctx.on_success_section

    verification.assert_true(on_success_value is None)
    return


# ---------------------------------------------------------------------------
# execute_tasklist
# ---------------------------------------------------------------------------


def test_execute_tasklist_with_empty_list_returns_zero() -> None:
    """An empty tasklist returns a zero result code."""

    jump_context = JumpContext()
    parameters: dict = {}
    tasklist: list = []

    result_code = execute_tasklist(_LOGGER, jump_context, parameters, tasklist)

    verification.assert_equal(result_code, 0)
    return


def test_execute_tasklist_with_single_gitcheckout_task_returns_zero() -> None:
    """A single GitCheckout task returns zero."""

    jump_context = JumpContext()
    parameters: dict = {}
    environment: dict = {}
    flowstate: dict = {}
    tasklist = [
        {"task": "demo", "tasktype": _GIT_TASKTYPE},
    ]

    result_code = execute_tasklist(
        _LOGGER,
        jump_context,
        parameters,
        tasklist,
        environment=environment,
        flowstate=flowstate,
    )

    verification.assert_equal(result_code, 0)
    return


def test_execute_tasklist_with_unknown_class_raises_configuration_error() -> None:
    """A tasktype referencing a non-existent class raises ConfigurationError."""

    jump_context = JumpContext()
    parameters: dict = {}
    tasklist = [
        {
            "task": "demo",
            "tasktype": "automojo.taskplus.tasks.gitcheckout@DoesNotExistClassName",
        },
    ]

    raised = False
    try:
        execute_tasklist(_LOGGER, jump_context, parameters, tasklist)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_execute_tasklist_with_empty_taskgroup_returns_zero() -> None:
    """
        A taskgroup descriptor with an empty ``items`` list returns zero
        (regression: the taskgroup branch must not NameError).
    """

    jump_context = JumpContext()
    parameters: dict = {}
    tasklist = [
        {
            "taskgroup": "outer",
            "items": [],
        },
    ]

    result_code = execute_tasklist(_LOGGER, jump_context, parameters, tasklist)

    verification.assert_equal(result_code, 0)
    return


def test_execute_tasklist_with_taskgroup_of_unknown_nodes_returns_zero() -> None:
    """
        A taskgroup whose ``items`` are unrecognized nodes (no 'task' or
        'taskgroup' keys) is silently traversed and returns zero.
    """

    jump_context = JumpContext()
    parameters: dict = {}
    tasklist = [
        {
            "taskgroup": "outer",
            "items": [
                {"notes": "neither task nor taskgroup"},
                {"more-notes": "still neither"},
            ],
        },
    ]

    result_code = execute_tasklist(_LOGGER, jump_context, parameters, tasklist)

    verification.assert_equal(result_code, 0)
    return


def test_execute_tasklist_with_unrecognized_node_returns_zero_silently() -> None:
    """A node with neither 'task' nor 'taskgroup' keys is silently skipped."""

    jump_context = JumpContext()
    parameters: dict = {}
    tasklist = [
        {"notes": "this node has neither task nor taskgroup"},
    ]

    result_code = execute_tasklist(_LOGGER, jump_context, parameters, tasklist)

    verification.assert_equal(result_code, 0)
    return


def test_execute_tasklist_with_ordinal_prefix_returns_zero() -> None:
    """Passing an ``ordinal_prefix`` does not affect a normal GitCheckout run."""

    jump_context = JumpContext()
    parameters: dict = {}
    environment: dict = {}
    flowstate: dict = {}
    tasklist = [
        {"task": "demo", "tasktype": _GIT_TASKTYPE},
    ]

    result_code = execute_tasklist(
        _LOGGER,
        jump_context,
        parameters,
        tasklist,
        ordinal_prefix="A",
        environment=environment,
        flowstate=flowstate,
    )

    verification.assert_equal(result_code, 0)
    return


# ---------------------------------------------------------------------------
# execute_workflow
# ---------------------------------------------------------------------------


def test_execute_workflow_with_empty_workflow_returns_zero() -> None:
    """An empty workflow with no environment and no tasks returns zero."""

    environment: dict = {}
    parameters: dict = {}
    workflow: list = []

    result_code = execute_workflow(
        _LOGGER, environment=environment, parameters=parameters, workflow=workflow
    )

    verification.assert_equal(result_code, 0)
    return


def test_execute_workflow_publishes_environment_variables() -> None:
    """
        execute_workflow copies the ``environment`` dict into ``os.environ``
        before executing the workflow.
    """

    env_key = "TASKPLUS_TEST_EXEC_ENV"
    env_value = "set"

    if env_key in os.environ:
        del os.environ[env_key]

    environment = {env_key: env_value}
    parameters: dict = {}
    workflow: list = []

    try:
        result_code = execute_workflow(
            _LOGGER,
            environment=environment,
            parameters=parameters,
            workflow=workflow,
        )

        was_set = env_key in os.environ
        observed_value = os.environ.get(env_key, None)

        verification.assert_equal(result_code, 0)
        verification.assert_equal(was_set, True)
        verification.assert_equal(observed_value, env_value)
    finally:
        if env_key in os.environ:
            del os.environ[env_key]

    return


