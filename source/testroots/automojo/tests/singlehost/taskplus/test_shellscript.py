"""Tests for the :class:`ShellScript` task class."""

from typing import Any, Dict, List

import logging
import tempfile

from automojo.testbase import verification

from automojo.runtime.optionoverrides import AM_RUNTIME_OPTION_OVERRIDES
from automojo.thisapp.persona import APP_PERSONA_ESTABLISHED, establish_app_persona

from automojo.taskplus.model.task import Task
from automojo.taskplus.tasks.shellscript import ShellScript


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


def _ensure_runtime_paths_configured() -> None:
    """
        Ensure the application persona is established and the output
        directory runtime variable is set so that
        :py:func:`automojo.runtime.paths.get_temporary_file` is able to
        resolve a temporary directory.
    """

    if not APP_PERSONA_ESTABLISHED:
        establish_app_persona(name="automojo-taskplus", logger_name="automojo-taskplus", log_basename="automojo-taskplus")

    output_dir = tempfile.mkdtemp(prefix="taskplus-test-output-")
    AM_RUNTIME_OPTION_OVERRIDES.override_output_directory(output_directory=output_dir)
    return


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_script_property() -> None:
    """Constructing :class:`ShellScript` stores the ``script`` from ``task_info``."""

    script_lines: List[str] = ["#!/usr/bin/env bash", "exit 0"]
    task_info: Dict[str, Any] = {"script": script_lines}
    task = ShellScript(ordinal="1", label="sh", task_info=task_info, logger=_make_logger())

    stored_script = task.script

    verification.assert_equal(stored_script, script_lines)
    return


def test_construct_is_a_task() -> None:
    """A :class:`ShellScript` instance is also a :class:`Task`."""

    task_info: Dict[str, Any] = {"script": ["exit 0"]}
    task = ShellScript(ordinal="1", label="sh", task_info=task_info, logger=_make_logger())

    is_task = isinstance(task, Task)

    verification.assert_equal(is_task, True)
    return


def test_construct_missing_script_key_raises_keyerror() -> None:
    """Constructing :class:`ShellScript` without a ``script`` key raises :class:`KeyError`."""

    raised = False
    try:
        ShellScript(ordinal="1", label="sh", task_info={}, logger=_make_logger())
    except KeyError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# perform_task
# ---------------------------------------------------------------------------


def test_perform_task_with_exit_zero_returns_zero() -> None:
    """:py:meth:`perform_task` writes the script to a temp file and returns the exit code."""

    _ensure_runtime_paths_configured()

    task_info: Dict[str, Any] = {"script": ["exit 0"]}
    task = ShellScript(ordinal="1", label="sh", task_info=task_info, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 0)
    return


def test_perform_task_with_exit_five_returns_five() -> None:
    """:py:meth:`perform_task` propagates a non-zero shell exit code."""

    _ensure_runtime_paths_configured()

    task_info: Dict[str, Any] = {"script": ["exit 5"]}
    task = ShellScript(ordinal="2", label="sh", task_info=task_info, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 5)
    return
