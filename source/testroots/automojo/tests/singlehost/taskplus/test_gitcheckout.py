"""Tests for the :class:`GitCheckout` task class."""

from typing import Any, Dict

import logging

from automojo.testbase import verification

from automojo.taskplus.model.flownode import FlowNode
from automojo.taskplus.model.task import Task
from automojo.taskplus.tasks.gitcheckout import GitCheckout


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_with_empty_task_info_succeeds() -> None:
    """Constructing :class:`GitCheckout` with an empty ``task_info`` dict succeeds."""

    task_info: Dict[str, Any] = {}
    task = GitCheckout(ordinal="0001", label="checkout", task_info=task_info, logger=_make_logger())

    is_not_none = task is not None
    verification.assert_equal(is_not_none, True)
    return


def test_construct_is_a_task_and_flownode() -> None:
    """A :class:`GitCheckout` instance is also a :class:`Task` and :class:`FlowNode`."""

    task = GitCheckout(ordinal="0001", label="checkout", task_info={}, logger=_make_logger())

    is_task = isinstance(task, Task)
    is_flownode = isinstance(task, FlowNode)

    verification.assert_equal(is_task, True)
    verification.assert_equal(is_flownode, True)
    return


def test_construct_stores_inherited_flownode_fields() -> None:
    """:class:`GitCheckout` exposes inherited :class:`FlowNode` fields."""

    task_info: Dict[str, Any] = {"if": "True"}
    task = GitCheckout(ordinal="0007", label="alpha", task_info=task_info, logger=_make_logger())

    verification.assert_equal(task.ordinal, "0007")
    verification.assert_equal(task.label, "alpha")
    verification.assert_equal(task.node_info, task_info)
    verification.assert_equal(task.if_expr, "True")
    return


# ---------------------------------------------------------------------------
# perform_task
# ---------------------------------------------------------------------------


def test_perform_task_returns_zero_with_empty_inputs() -> None:
    """:py:meth:`GitCheckout.perform_task` returns ``0`` for empty inputs."""

    task = GitCheckout(ordinal="0001", label="checkout", task_info={}, logger=_make_logger())

    exit_code = task.perform_task(environment={}, parameters={}, flowstate={})

    verification.assert_equal(exit_code, 0)
    return


def test_perform_task_returns_zero_with_populated_inputs() -> None:
    """:py:meth:`GitCheckout.perform_task` ignores its inputs and returns ``0``."""

    task = GitCheckout(ordinal="0001", label="checkout", task_info={}, logger=_make_logger())

    environment: Dict[str, str] = {"PATH": "/usr/bin"}
    parameters: Dict[str, Any] = {"branch": "main"}
    flowstate: Dict[str, Any] = {"prior": "ok"}

    exit_code = task.perform_task(environment=environment, parameters=parameters, flowstate=flowstate)

    verification.assert_equal(exit_code, 0)
    return
