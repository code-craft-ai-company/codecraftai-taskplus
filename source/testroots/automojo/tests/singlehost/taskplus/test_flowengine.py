"""Tests for :class:`JumpContext` and :class:`FlowEngine`."""

from typing import Any, Dict, List, Optional, Tuple

import logging

from automojo.testbase import verification

from automojo.taskplus.model.flowengine import FlowEngine, JumpContext
from automojo.taskplus.model.task import Task
from automojo.taskplus.model.taskgroup import TaskGroup
from automojo.taskplus.model.workflow import Workflow


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test-flowengine")
    return rtnval


class _RecordingTask(Task):
    """
        Concrete :class:`Task` subclass that records each call to
        ``perform_task`` and returns a configurable result code.
    """

    def __init__(self, ordinal: str, label: str, node_info: Dict[str, Any], logger: logging.Logger,
                 return_code: int = 0):
        super().__init__(ordinal, label, node_info, logger)
        self._calls: List[Tuple[Dict[str, str], Dict[str, Any], Dict[str, Any]]] = []
        self._return_code = return_code
        return

    @property
    def calls(self) -> List[Tuple[Dict[str, str], Dict[str, Any], Dict[str, Any]]]:
        return self._calls

    @property
    def call_count(self) -> int:
        rtnval = len(self._calls)
        return rtnval

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]],
                     flowstate: Dict[str, Any]) -> int:
        self._calls.append((environment, parameters, flowstate))
        rtnval = self._return_code
        return rtnval


def _make_task(label: str, ordinal: str = "1", return_code: int = 0,
               node_info: Optional[Dict[str, Any]] = None) -> _RecordingTask:
    """
        Build a :class:`_RecordingTask` with the supplied configuration.

        :param label: The task label.
        :param ordinal: The ordinal string for the task.
        :param return_code: The return code that ``perform_task`` will produce.
        :param node_info: Optional node_info dict (defaults to ``{}``).

        :returns: A new :class:`_RecordingTask` instance.
    """
    if node_info is None:
        node_info = {}

    rtnval = _RecordingTask(ordinal=ordinal, label=label, node_info=node_info,
                            logger=_make_logger(), return_code=return_code)
    return rtnval


# ---------------------------------------------------------------------------
# JumpContext
# ---------------------------------------------------------------------------


def test_jump_context_initial_seeking_node_is_none() -> None:
    """A fresh :class:`JumpContext` has ``seeking_node`` set to ``None``."""

    ctx = JumpContext()

    seeking_value = ctx.seeking_node

    verification.assert_equal(seeking_value, None)
    return


def test_jump_context_seeking_node_can_be_assigned() -> None:
    """The :py:attr:`seeking_node` field can be assigned a node label."""

    ctx = JumpContext()

    ctx.seeking_node = "rescue"

    verification.assert_equal(ctx.seeking_node, "rescue")
    return


# ---------------------------------------------------------------------------
# FlowEngine.evaluate_expression
# ---------------------------------------------------------------------------


def test_evaluate_expression_simple_true_literal_returns_true() -> None:
    """``evaluate_expression`` returns ``True`` for the literal 'True'."""

    engine = FlowEngine()

    result_value = engine.evaluate_expression(if_expr="True", environment={}, parameters={})

    verification.assert_equal(result_value, True)
    return


def test_evaluate_expression_simple_false_literal_returns_false() -> None:
    """``evaluate_expression`` returns ``False`` for the literal 'False'."""

    engine = FlowEngine()

    result_value = engine.evaluate_expression(if_expr="False", environment={}, parameters={})

    verification.assert_equal(result_value, False)
    return


def test_evaluate_expression_arithmetic_equality_returns_true() -> None:
    """``evaluate_expression`` returns ``True`` for '1 + 1 == 2'."""

    engine = FlowEngine()

    result_value = engine.evaluate_expression(if_expr="1 + 1 == 2", environment={}, parameters={})

    verification.assert_equal(result_value, True)
    return


def test_evaluate_expression_can_read_flowstate() -> None:
    """``evaluate_expression`` exposes the engine ``_flowstate`` as a local named ``flowstate``."""

    engine = FlowEngine()
    engine._flowstate = {"key": "value"}

    result_value = engine.evaluate_expression(
        if_expr="flowstate['key'] == 'value'",
        environment={},
        parameters={},
    )

    verification.assert_equal(result_value, True)
    return


def test_evaluate_expression_can_read_environment() -> None:
    """``evaluate_expression`` exposes the ``environment`` parameter to the expression."""

    engine = FlowEngine()

    result_value = engine.evaluate_expression(
        if_expr="environment['VAR'] == 'X'",
        environment={"VAR": "X"},
        parameters={},
    )

    verification.assert_equal(result_value, True)
    return


def test_evaluate_expression_can_read_parameters() -> None:
    """``evaluate_expression`` exposes the ``parameters`` parameter to the expression."""

    engine = FlowEngine()

    result_value = engine.evaluate_expression(
        if_expr="parameters['count'] == 3",
        environment={},
        parameters={"count": 3},
    )

    verification.assert_equal(result_value, True)
    return


# ---------------------------------------------------------------------------
# FlowEngine.execute - basic success / failure
# ---------------------------------------------------------------------------


def test_execute_returns_zero_when_all_tasks_succeed() -> None:
    """Executing a workflow with all-success tasks yields a result of 0."""

    task_a = _make_task(label="a", ordinal="1", return_code=0)
    task_b = _make_task(label="b", ordinal="2", return_code=0)
    workflow = Workflow(environment={}, parameters={}, flow=[task_a, task_b])

    engine = FlowEngine()

    result_code = engine.execute(workflow=workflow)

    verification.assert_equal(result_code, 0)
    verification.assert_equal(task_a.call_count, 1)
    verification.assert_equal(task_b.call_count, 1)
    return


def test_execute_runs_each_task_exactly_once_for_simple_flow() -> None:
    """Each task in a simple flat flow must be invoked exactly once."""

    task_a = _make_task(label="a", ordinal="1", return_code=0)
    task_b = _make_task(label="b", ordinal="2", return_code=0)
    task_c = _make_task(label="c", ordinal="3", return_code=0)
    workflow = Workflow(environment={}, parameters={}, flow=[task_a, task_b, task_c])

    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(task_a.call_count, 1)
    verification.assert_equal(task_b.call_count, 1)
    verification.assert_equal(task_c.call_count, 1)
    return


def test_execute_passes_environment_and_parameters_to_task() -> None:
    """The environment and parameters passed in the workflow reach the task."""

    environment: Dict[str, str] = {"K": "V"}
    parameters: Dict[str, Any] = {"alpha": 7}
    task_a = _make_task(label="a", ordinal="1", return_code=0)
    workflow = Workflow(environment=environment, parameters=parameters, flow=[task_a])

    engine = FlowEngine()

    engine.execute(workflow=workflow)

    only_call = task_a.calls[0]
    seen_env = only_call[0]
    seen_params = only_call[1]

    verification.assert_equal(seen_env, environment)
    verification.assert_equal(seen_params, parameters)
    return


# ---------------------------------------------------------------------------
# FlowEngine.execute - if_expr conditional skipping
# ---------------------------------------------------------------------------


def test_execute_skips_task_when_if_expr_is_false() -> None:
    """A task whose ``if`` expression evaluates to ``False`` must not be invoked."""

    skip_node_info: Dict[str, Any] = {"if": "False"}
    task_skip = _make_task(label="skip-me", ordinal="1", return_code=0, node_info=skip_node_info)
    workflow = Workflow(environment={}, parameters={}, flow=[task_skip])

    engine = FlowEngine()

    result_code = engine.execute(workflow=workflow)

    verification.assert_equal(result_code, 0)
    verification.assert_equal(task_skip.call_count, 0)
    return


def test_execute_runs_task_when_if_expr_is_true() -> None:
    """A task whose ``if`` expression evaluates to ``True`` must be invoked."""

    run_node_info: Dict[str, Any] = {"if": "True"}
    task_run = _make_task(label="run-me", ordinal="1", return_code=0, node_info=run_node_info)
    workflow = Workflow(environment={}, parameters={}, flow=[task_run])

    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(task_run.call_count, 1)
    return


# ---------------------------------------------------------------------------
# FlowEngine.execute - task group recursion
# ---------------------------------------------------------------------------


def test_execute_recurses_into_taskgroup_items() -> None:
    """``execute`` must recurse into a :class:`TaskGroup` and invoke its items."""

    inner_a = _make_task(label="inner-a", ordinal="1.1", return_code=0)
    inner_b = _make_task(label="inner-b", ordinal="1.2", return_code=0)
    group = TaskGroup(ordinal="1", label="grp", node_info={}, items=[inner_a, inner_b],
                      logger=_make_logger())

    workflow = Workflow(environment={}, parameters={}, flow=[group])
    engine = FlowEngine()

    result_code = engine.execute(workflow=workflow)

    verification.assert_equal(result_code, 0)
    verification.assert_equal(inner_a.call_count, 1)
    verification.assert_equal(inner_b.call_count, 1)
    return


def test_execute_recurses_into_deeply_nested_taskgroup() -> None:
    """``execute`` must recurse through multiple :class:`TaskGroup` levels."""

    deep_task = _make_task(label="deep", ordinal="1.1.1", return_code=0)
    inner_group = TaskGroup(ordinal="1.1", label="inner", node_info={}, items=[deep_task],
                            logger=_make_logger())
    outer_group = TaskGroup(ordinal="1", label="outer", node_info={}, items=[inner_group],
                            logger=_make_logger())

    workflow = Workflow(environment={}, parameters={}, flow=[outer_group])
    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(deep_task.call_count, 1)
    return


# ---------------------------------------------------------------------------
# FlowEngine.execute - onfailure / onsuccess jump semantics
# ---------------------------------------------------------------------------


def test_execute_onfailure_jumps_to_named_node_and_skips_others() -> None:
    """A failing task with ``onfailure: rescue`` must skip subsequent tasks until 'rescue'."""

    fail_node_info: Dict[str, Any] = {"onfailure": "rescue"}
    failing_task = _make_task(label="failer", ordinal="1", return_code=1,
                              node_info=fail_node_info)
    skipped_task = _make_task(label="skipped", ordinal="2", return_code=0)
    rescue_task = _make_task(label="rescue", ordinal="3", return_code=0)
    after_rescue = _make_task(label="after", ordinal="4", return_code=0)

    flow_items = [failing_task, skipped_task, rescue_task, after_rescue]
    workflow = Workflow(environment={}, parameters={}, flow=flow_items)
    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(failing_task.call_count, 1)
    verification.assert_equal(skipped_task.call_count, 0)
    verification.assert_equal(rescue_task.call_count, 1)
    verification.assert_equal(after_rescue.call_count, 1)
    return


def test_execute_onsuccess_jumps_to_named_node_and_skips_others() -> None:
    """A succeeding task with ``onsuccess: target`` must skip subsequent tasks until 'target'."""

    success_node_info: Dict[str, Any] = {"onsuccess": "target"}
    succ_task = _make_task(label="succ", ordinal="1", return_code=0,
                           node_info=success_node_info)
    skipped_task = _make_task(label="skipped", ordinal="2", return_code=0)
    target_task = _make_task(label="target", ordinal="3", return_code=0)
    after_target = _make_task(label="after", ordinal="4", return_code=0)

    flow_items = [succ_task, skipped_task, target_task, after_target]
    workflow = Workflow(environment={}, parameters={}, flow=flow_items)
    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(succ_task.call_count, 1)
    verification.assert_equal(skipped_task.call_count, 0)
    verification.assert_equal(target_task.call_count, 1)
    verification.assert_equal(after_target.call_count, 1)
    return


def test_execute_onfailure_without_handler_does_not_jump() -> None:
    """A failing task without an ``onfailure`` field does not alter execution flow."""

    failing_task = _make_task(label="failer", ordinal="1", return_code=1)
    next_task = _make_task(label="next", ordinal="2", return_code=0)
    workflow = Workflow(environment={}, parameters={}, flow=[failing_task, next_task])
    engine = FlowEngine()

    result_code = engine.execute(workflow=workflow)

    verification.assert_equal(failing_task.call_count, 1)
    verification.assert_equal(next_task.call_count, 1)
    verification.assert_equal(result_code, 0)
    return


def test_execute_onsuccess_without_handler_does_not_jump() -> None:
    """A succeeding task without an ``onsuccess`` field falls through normally."""

    succ_task = _make_task(label="succ", ordinal="1", return_code=0)
    next_task = _make_task(label="next", ordinal="2", return_code=0)
    workflow = Workflow(environment={}, parameters={}, flow=[succ_task, next_task])
    engine = FlowEngine()

    engine.execute(workflow=workflow)

    verification.assert_equal(succ_task.call_count, 1)
    verification.assert_equal(next_task.call_count, 1)
    return


def test_execute_with_empty_flow_returns_zero() -> None:
    """Executing a workflow with no flow items yields a result of 0."""

    workflow = Workflow(environment={}, parameters={}, flow=[])
    engine = FlowEngine()

    result_code = engine.execute(workflow=workflow)

    verification.assert_equal(result_code, 0)
    return
