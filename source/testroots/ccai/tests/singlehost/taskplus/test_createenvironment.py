"""Tests for the :class:`CreateEnvironment` task class."""

from typing import Any, Dict, List

import logging
import os

from ccai.testbase import verification

from ccai.taskplus.model.task import Task
from ccai.taskplus.tasks.createenvironment import CreateEnvironment


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_variables_property() -> None:
    """Constructing :class:`CreateEnvironment` stores the ``variables`` from ``task_info``."""

    variables: List[Dict[str, str]] = [{"name": "FOO", "value": "/tmp/foo"}]
    task_info: Dict[str, Any] = {"variables": variables}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    stored_variables = task.variables

    verification.assert_equal(stored_variables, variables)
    return


def test_construct_is_a_task() -> None:
    """A :class:`CreateEnvironment` instance is also a :class:`Task`."""

    task_info: Dict[str, Any] = {"variables": []}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    is_task = isinstance(task, Task)

    verification.assert_equal(is_task, True)
    return


def test_construct_missing_variables_key_raises_keyerror() -> None:
    """Constructing :class:`CreateEnvironment` without a ``variables`` key raises :class:`KeyError`."""

    raised = False
    try:
        CreateEnvironment(ordinal="0001", label="env", task_info={}, logger=_make_logger())
    except KeyError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# perform_task - value branch
# ---------------------------------------------------------------------------


def test_perform_task_with_value_sets_environment_variable() -> None:
    """:py:meth:`perform_task` with a ``value`` entry sets the env var and returns ``0``."""

    var_name = "TASKPLUS_TEST_VAR_VALUE"
    variables: List[Dict[str, str]] = [{"name": var_name, "value": "/tmp/foo"}]
    task_info: Dict[str, Any] = {"variables": variables}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    try:
        status_code = task.perform_task(environment={}, parameters={}, flowstate={})

        env_value = os.environ.get(var_name)

        verification.assert_equal(status_code, 0)
        verification.assert_equal(env_value, "/tmp/foo")
    finally:
        if var_name in os.environ:
            del os.environ[var_name]
    return


def test_perform_task_value_branch_applies_expanduser_and_expandvars() -> None:
    """:py:meth:`perform_task` applies :py:func:`os.path.expanduser` and :py:func:`os.path.expandvars` to the value."""

    helper_var = "TASKPLUS_TMP_FOO"
    target_var = "TASKPLUS_TEST_VAR_EXPANDED"

    os.environ[helper_var] = "BAR"

    variables: List[Dict[str, str]] = [{"name": target_var, "value": "$TASKPLUS_TMP_FOO/x"}]
    task_info: Dict[str, Any] = {"variables": variables}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    try:
        status_code = task.perform_task(environment={}, parameters={}, flowstate={})

        env_value = os.environ.get(target_var)

        verification.assert_equal(status_code, 0)
        verification.assert_equal(env_value, "BAR/x")
    finally:
        if target_var in os.environ:
            del os.environ[target_var]
        if helper_var in os.environ:
            del os.environ[helper_var]
    return


# ---------------------------------------------------------------------------
# perform_task - command branch
# ---------------------------------------------------------------------------


def test_perform_task_with_command_sets_stripped_stdout_as_value() -> None:
    """:py:meth:`perform_task` with a ``command`` entry sets the env var to stripped stdout."""

    var_name = "TASKPLUS_TEST_VAR_CMD"
    variables: List[Dict[str, str]] = [{"name": var_name, "command": "echo hello"}]
    task_info: Dict[str, Any] = {"variables": variables}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    try:
        status_code = task.perform_task(environment={}, parameters={}, flowstate={})

        env_value = os.environ.get(var_name)

        verification.assert_equal(status_code, 0)
        verification.assert_equal(env_value, "hello")
    finally:
        if var_name in os.environ:
            del os.environ[var_name]
    return


# ---------------------------------------------------------------------------
# perform_task - missing both command and value
# ---------------------------------------------------------------------------


def test_perform_task_with_missing_value_and_command_does_not_raise() -> None:
    """A variable info missing both ``command`` and ``value`` does not raise, is not
    set, and reports a non-zero status code (the malformed entry is a failure)."""

    var_name = "TASKPLUS_TEST_VAR_NEITHER"

    if var_name in os.environ:
        del os.environ[var_name]

    variables: List[Dict[str, Any]] = [{"name": var_name}]
    task_info: Dict[str, Any] = {"variables": variables}
    task = CreateEnvironment(ordinal="0001", label="env", task_info=task_info, logger=_make_logger())

    raised = False
    status_code = -1
    try:
        try:
            status_code = task.perform_task(environment={}, parameters={}, flowstate={})
        except Exception:
            raised = True

        is_set = var_name in os.environ

        verification.assert_equal(raised, False)
        verification.assert_equal(status_code, 1)
        verification.assert_equal(is_set, False)
    finally:
        if var_name in os.environ:
            del os.environ[var_name]
    return
