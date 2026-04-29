"""Tests for the :class:`Task` base class."""

from typing import Any, Dict, Optional

import logging

from automojo.testbase import verification

from automojo.errors.exceptions import AbstractMethodError

from automojo.taskplus.model.flownode import FlowNode
from automojo.taskplus.model.task import Task


class _RecordingTask(Task):
    """
        Minimal concrete subclass of :class:`Task` whose
        :py:meth:`perform_task` records its arguments and returns a
        configurable integer result.
    """

    def __init__(self, ordinal: str, label: str, node_info: Dict[str, Any], logger: logging.Logger, return_value: int = 0):
        super().__init__(ordinal=ordinal, label=label, node_info=node_info, logger=logger)
        self._return_value = return_value
        self._last_environment: Optional[Dict[str, str]] = None
        self._last_parameters: Optional[Dict[str, Any]] = None
        self._last_flowstate: Optional[Dict[str, Any]] = None
        self._call_count = 0
        return

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:
        self._last_environment = environment
        self._last_parameters = parameters
        self._last_flowstate = flowstate
        self._call_count += 1
        rtnval = self._return_value
        return rtnval


class _BubbleAbstractTask(Task):
    """
        Minimal concrete subclass of :class:`Task` whose
        :py:meth:`perform_task` calls into the abstract base implementation
        in order to surface :class:`AbstractMethodError`.
    """

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:
        rtnval = super().perform_task(environment=environment, parameters=parameters, flowstate=flowstate)
        return rtnval


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_flownode_fields() -> None:
    """Constructing a Task initializes all inherited FlowNode fields."""

    node_info: Dict[str, Any] = {"if": "True"}
    task = _RecordingTask(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    verification.assert_equal(task.ordinal, "0001")
    verification.assert_equal(task.label, "alpha")
    verification.assert_equal(task.node_info, node_info)
    verification.assert_equal(task.if_expr, "True")
    return


def test_task_is_a_flownode() -> None:
    """A :class:`Task` instance is also a :class:`FlowNode`."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())

    is_flownode = isinstance(task, FlowNode)

    verification.assert_equal(is_flownode, True)
    return


def test_task_cannot_be_instantiated_directly() -> None:
    """The :class:`Task` base class is abstract and cannot be instantiated directly."""

    raised = False
    try:
        Task(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())
    except TypeError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# onfailure / onsuccess properties
# ---------------------------------------------------------------------------


def test_onfailure_property_returns_value_when_key_present() -> None:
    """When ``node_info`` contains an ``onfailure`` key, :py:attr:`onfailure` returns its value."""

    node_info: Dict[str, Any] = {"onfailure": "rescue"}
    task = _RecordingTask(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    onfailure_value = task.onfailure

    verification.assert_equal(onfailure_value, "rescue")
    return


def test_onfailure_property_returns_none_when_key_absent() -> None:
    """When ``node_info`` does not contain an ``onfailure`` key, :py:attr:`onfailure` returns ``None``."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())

    onfailure_value = task.onfailure

    verification.assert_equal(onfailure_value, None)
    return


def test_onsuccess_property_returns_value_when_key_present() -> None:
    """When ``node_info`` contains an ``onsuccess`` key, :py:attr:`onsuccess` returns its value."""

    node_info: Dict[str, Any] = {"onsuccess": "next"}
    task = _RecordingTask(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    onsuccess_value = task.onsuccess

    verification.assert_equal(onsuccess_value, "next")
    return


def test_onsuccess_property_returns_none_when_key_absent() -> None:
    """When ``node_info`` does not contain an ``onsuccess`` key, :py:attr:`onsuccess` returns ``None``."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())

    onsuccess_value = task.onsuccess

    verification.assert_equal(onsuccess_value, None)
    return


# ---------------------------------------------------------------------------
# execute() proxies to perform_task()
# ---------------------------------------------------------------------------


def test_execute_invokes_perform_task_once() -> None:
    """:py:meth:`Task.execute` invokes :py:meth:`perform_task` exactly once."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger(), return_value=0)

    task.execute(environment={}, parameters={}, flowstate={})
    call_count = task._call_count

    verification.assert_equal(call_count, 1)
    return


def test_execute_returns_value_from_perform_task() -> None:
    """:py:meth:`Task.execute` returns the value returned by :py:meth:`perform_task`."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger(), return_value=42)

    result = task.execute(environment={}, parameters={}, flowstate={})

    verification.assert_equal(result, 42)
    return


def test_execute_passes_environment_through_to_perform_task() -> None:
    """:py:meth:`Task.execute` passes the ``environment`` argument through unchanged."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())
    environment: Dict[str, str] = {"PATH": "/usr/bin"}

    task.execute(environment=environment, parameters={}, flowstate={})
    received = task._last_environment

    verification.assert_equal(received, environment)
    return


def test_execute_passes_parameters_through_to_perform_task() -> None:
    """:py:meth:`Task.execute` passes the ``parameters`` argument through unchanged."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())
    parameters: Dict[str, Any] = {"alpha": 1}

    task.execute(environment={}, parameters=parameters, flowstate={})
    received = task._last_parameters

    verification.assert_equal(received, parameters)
    return


def test_execute_passes_flowstate_through_to_perform_task() -> None:
    """:py:meth:`Task.execute` passes the ``flowstate`` argument through unchanged."""

    task = _RecordingTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())
    flowstate: Dict[str, Any] = {"prior": "ok"}

    task.execute(environment={}, parameters={}, flowstate=flowstate)
    received = task._last_flowstate

    verification.assert_equal(received, flowstate)
    return


# ---------------------------------------------------------------------------
# Abstract perform_task surfaces AbstractMethodError when invoked via super()
# ---------------------------------------------------------------------------


def test_abstract_perform_task_raises_abstract_method_error() -> None:
    """Invoking the abstract base implementation of perform_task raises AbstractMethodError."""

    task = _BubbleAbstractTask(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())

    raised = False
    try:
        task.execute(environment={}, parameters={}, flowstate={})
    except AbstractMethodError:
        raised = True

    verification.assert_equal(raised, True)
    return
