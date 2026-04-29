"""Tests for the :class:`RunCommand` task class."""

from typing import Any, Dict

import logging

from automojo.testbase import verification

from automojo.taskplus.model.task import Task
from automojo.taskplus.tasks.runcommand import RunCommand


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_command_property() -> None:
    """Constructing :class:`RunCommand` stores the ``command`` from ``task_info``."""

    task_info: Dict[str, Any] = {"command": "echo hello"}
    task = RunCommand(ordinal="0001", label="cmd", task_info=task_info, logger=_make_logger())

    stored_command = task.command

    verification.assert_equal(stored_command, "echo hello")
    return


def test_construct_is_a_task() -> None:
    """A :class:`RunCommand` instance is also a :class:`Task`."""

    task_info: Dict[str, Any] = {"command": "exit 0"}
    task = RunCommand(ordinal="0001", label="cmd", task_info=task_info, logger=_make_logger())

    is_task = isinstance(task, Task)

    verification.assert_equal(is_task, True)
    return


def test_construct_missing_command_key_raises_keyerror() -> None:
    """Constructing :class:`RunCommand` without a ``command`` key raises :class:`KeyError`."""

    raised = False
    try:
        RunCommand(ordinal="0001", label="cmd", task_info={}, logger=_make_logger())
    except KeyError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# perform_task
# ---------------------------------------------------------------------------


def test_perform_task_with_exit_zero_returns_zero() -> None:
    """:py:meth:`perform_task` returns ``0`` when the command exits successfully."""

    task_info: Dict[str, Any] = {"command": "exit 0"}
    task = RunCommand(ordinal="0001", label="cmd", task_info=task_info, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 0)
    return


def test_perform_task_with_exit_seven_returns_seven() -> None:
    """:py:meth:`perform_task` returns the command's exit code (``7``)."""

    task_info: Dict[str, Any] = {"command": "exit 7"}
    task = RunCommand(ordinal="0001", label="cmd", task_info=task_info, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 7)
    return


def test_perform_task_with_echo_returns_zero() -> None:
    """:py:meth:`perform_task` returns ``0`` for a simple ``echo`` command."""

    task_info: Dict[str, Any] = {"command": "echo hello"}
    task = RunCommand(ordinal="0001", label="cmd", task_info=task_info, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 0)
    return
