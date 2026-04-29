"""Tests for the :class:`EmbeddedPython` task class."""

from typing import Any, Dict, List

import logging

from automojo.testbase import verification

from automojo.taskplus.model.task import Task
from automojo.taskplus.tasks.embeddedpython import EmbeddedPython


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_script_property() -> None:
    """Constructing :class:`EmbeddedPython` stores the ``script`` from ``task_info``."""

    script_lines: List[str] = ["x = 1 + 1", "y = x + 2"]
    task_info: Dict[str, Any] = {"script": script_lines}
    task = EmbeddedPython(ordinal="0001", label="py", task_info=task_info, logger=_make_logger())

    stored_script = task.script

    verification.assert_equal(stored_script, script_lines)
    return


def test_construct_is_a_task() -> None:
    """An :class:`EmbeddedPython` instance is also a :class:`Task`."""

    task = EmbeddedPython(ordinal="0001", label="py", task_info={"script": []}, logger=_make_logger())

    is_task = isinstance(task, Task)

    verification.assert_equal(is_task, True)
    return


def test_construct_missing_script_key_raises_keyerror() -> None:
    """Constructing :class:`EmbeddedPython` without a ``script`` key raises :class:`KeyError`."""

    raised = False
    try:
        EmbeddedPython(ordinal="0001", label="py", task_info={}, logger=_make_logger())
    except KeyError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# perform_task
# ---------------------------------------------------------------------------


def test_perform_task_with_simple_assignment_returns_zero() -> None:
    """:py:meth:`perform_task` returns ``0`` when the inline script executes successfully."""

    task_info: Dict[str, Any] = {"script": ["x = 1 + 1"]}
    task = EmbeddedPython(ordinal="0001", label="py", task_info=task_info, logger=_make_logger())

    exit_status = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_status, 0)
    return


def test_perform_task_with_raising_script_returns_one() -> None:
    """:py:meth:`perform_task` returns ``1`` when the script raises (bare ``except`` swallows it)."""

    task_info: Dict[str, Any] = {"script": ["raise ValueError('boom')"]}
    task = EmbeddedPython(ordinal="0001", label="py", task_info=task_info, logger=_make_logger())

    exit_status = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_status, 1)
    return


def test_perform_task_with_empty_script_returns_zero() -> None:
    """:py:meth:`perform_task` returns ``0`` for an empty script list."""

    task_info: Dict[str, Any] = {"script": []}
    task = EmbeddedPython(ordinal="0001", label="py", task_info=task_info, logger=_make_logger())

    exit_status = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_status, 0)
    return
