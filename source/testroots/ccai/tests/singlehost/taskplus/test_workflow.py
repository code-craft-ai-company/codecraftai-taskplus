"""Tests for the :class:`Workflow` class and its YAML parser."""

from typing import Any, Dict, List

from io import StringIO

from ccai.testbase import verification

from ccai.errors.exceptions import ConfigurationError

from ccai.taskplus.model.flownode import FlowNode
from ccai.taskplus.model.task import Task
from ccai.taskplus.model.taskgroup import TaskGroup
from ccai.taskplus.model.workflow import Workflow


_GIT_TASKTYPE = "ccai.taskplus.tasks.gitcheckout@GitCheckout"


def _basic_yaml(extra: str = "") -> str:
    """
        Build a minimal valid workflow YAML document with a single task.

        :param extra: Additional YAML lines (already indented) to append.

        :returns: The composed YAML document text.
    """
    yaml_lines = [
        "name: simple-workflow",
        "environment:",
        "  ENV_VAR: value",
        "parameters:",
        "  param_one: 1",
        "flow:",
        "  - task: do-it",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]

    if len(extra) > 0:
        yaml_lines.append(extra)

    rtnval = "\n".join(yaml_lines)
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_environment_parameters_and_flow() -> None:
    """Constructing a Workflow stores the environment, parameters, and flow."""

    environment: Dict[str, str] = {"K": "V"}
    parameters: Dict[str, Any] = {"alpha": 1}
    flow: List[FlowNode] = []

    workflow = Workflow(environment=environment, parameters=parameters, flow=flow)

    verification.assert_equal(workflow.environment, environment)
    verification.assert_equal(workflow.parameters, parameters)
    verification.assert_equal(workflow.flow, flow)
    return


def test_environment_property_returns_same_object() -> None:
    """The :py:attr:`environment` property returns the constructed dict instance."""

    environment: Dict[str, str] = {"K": "V"}
    workflow = Workflow(environment=environment, parameters={}, flow=[])

    is_same = workflow.environment is environment

    verification.assert_equal(is_same, True)
    return


def test_parameters_property_returns_same_object() -> None:
    """The :py:attr:`parameters` property returns the constructed dict instance."""

    parameters: Dict[str, Any] = {"alpha": 1}
    workflow = Workflow(environment={}, parameters=parameters, flow=[])

    is_same = workflow.parameters is parameters

    verification.assert_equal(is_same, True)
    return


def test_flow_property_returns_same_object() -> None:
    """The :py:attr:`flow` property returns the constructed list instance."""

    flow: List[FlowNode] = []
    workflow = Workflow(environment={}, parameters={}, flow=flow)

    is_same = workflow.flow is flow

    verification.assert_equal(is_same, True)
    return


# ---------------------------------------------------------------------------
# parse() - happy path
# ---------------------------------------------------------------------------


def test_parse_valid_yaml_returns_workflow_with_expected_environment() -> None:
    """Parsing a valid YAML doc yields a Workflow whose environment matches."""

    yaml_text = _basic_yaml()
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    env_value = workflow.environment

    verification.assert_equal(env_value, {"ENV_VAR": "value"})
    return


def test_parse_valid_yaml_returns_workflow_with_expected_parameters() -> None:
    """Parsing a valid YAML doc yields a Workflow whose parameters match."""

    yaml_text = _basic_yaml()
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    params_value = workflow.parameters

    verification.assert_equal(params_value, {"param_one": 1})
    return


def test_parse_valid_yaml_returns_workflow_with_one_task() -> None:
    """Parsing a YAML doc with a single task yields a flow of length 1."""

    yaml_text = _basic_yaml()
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    flow_len = len(workflow.flow)

    verification.assert_equal(flow_len, 1)
    return


def test_parse_single_task_has_label_and_ordinal_one() -> None:
    """The single parsed task has the YAML label and ordinal '1'."""

    yaml_text = _basic_yaml()
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    only_node = workflow.flow[0]
    is_task = isinstance(only_node, Task)

    verification.assert_equal(is_task, True)
    verification.assert_equal(only_node.label, "do-it")
    verification.assert_equal(only_node.ordinal, "1")
    return


def test_parse_omitting_environment_returns_empty_environment_dict() -> None:
    """If the YAML doc omits 'environment', the parsed Workflow has an empty env dict."""

    yaml_lines = [
        "name: no-env",
        "flow:",
        "  - task: do-it",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    env_value = workflow.environment

    verification.assert_equal(env_value, {})
    return


def test_parse_omitting_parameters_returns_empty_parameters_dict() -> None:
    """If the YAML doc omits 'parameters', the parsed Workflow has an empty parameters dict."""

    yaml_lines = [
        "name: no-params",
        "flow:",
        "  - task: do-it",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    params_value = workflow.parameters

    verification.assert_equal(params_value, {})
    return


# ---------------------------------------------------------------------------
# parse() - error cases
# ---------------------------------------------------------------------------


def test_parse_omitting_name_raises_configuration_error() -> None:
    """A YAML doc missing 'name' must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "flow:",
        "  - task: do-it",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_parse_omitting_flow_raises_configuration_error() -> None:
    """A YAML doc missing 'flow' must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "name: needs-flow",
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_parse_node_with_both_task_and_taskgroup_raises_configuration_error() -> None:
    """A node with both 'task' and 'taskgroup' keys must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "name: bad-node",
        "flow:",
        "  - task: do-it",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
        "    taskgroup: oops",
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_parse_taskgroup_missing_items_raises_configuration_error() -> None:
    """A 'taskgroup' node without 'items' must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "name: bad-taskgroup",
        "flow:",
        "  - taskgroup: my-group",
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_parse_node_with_neither_task_nor_taskgroup_raises_configuration_error() -> None:
    """A node missing both 'task' and 'taskgroup' must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "name: unknown-node",
        "flow:",
        "  - notes: this is not a real flow node",
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


def test_parse_task_with_unknown_class_in_module_raises_configuration_error() -> None:
    """A 'task' node whose tasktype names a missing class must raise :class:`ConfigurationError`."""

    yaml_lines = [
        "name: bad-class",
        "flow:",
        "  - task: do-it",
        "    tasktype: ccai.taskplus.tasks.gitcheckout@DoesNotExist",
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    raised = False
    try:
        Workflow.parse(workflow_stream=stream)
    except ConfigurationError:
        raised = True

    verification.assert_equal(raised, True)
    return


# ---------------------------------------------------------------------------
# parse() - ordinal assignment
# ---------------------------------------------------------------------------


def test_parse_three_top_level_tasks_get_ordinals_one_two_three() -> None:
    """Three top-level tasks must have ordinals '1', '2', '3' in order."""

    yaml_lines = [
        "name: three-tasks",
        "flow:",
        "  - task: t1",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
        "  - task: t2",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
        "  - task: t3",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    flow = workflow.flow

    verification.assert_equal(len(flow), 3)
    verification.assert_equal(flow[0].ordinal, "1")
    verification.assert_equal(flow[1].ordinal, "2")
    verification.assert_equal(flow[2].ordinal, "3")
    return


def test_parse_three_top_level_tasks_preserve_labels_in_order() -> None:
    """Three top-level tasks must preserve labels in order."""

    yaml_lines = [
        "name: three-tasks-labels",
        "flow:",
        "  - task: alpha",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
        "  - task: beta",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
        "  - task: gamma",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    flow = workflow.flow

    verification.assert_equal(flow[0].label, "alpha")
    verification.assert_equal(flow[1].label, "beta")
    verification.assert_equal(flow[2].label, "gamma")
    return


def test_parse_nested_taskgroup_yields_taskgroup_instance() -> None:
    """A nested 'taskgroup' must produce a :class:`TaskGroup` at the top level."""

    yaml_lines = [
        "name: nested",
        "flow:",
        "  - taskgroup: outer-group",
        "    items:",
        "      - task: child-a",
        "        tasktype: {0}".format(_GIT_TASKTYPE),
        "      - task: child-b",
        "        tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    only_node = workflow.flow[0]
    is_group = isinstance(only_node, TaskGroup)

    verification.assert_equal(is_group, True)
    verification.assert_equal(only_node.label, "outer-group")
    verification.assert_equal(only_node.ordinal, "1")
    return


def test_parse_nested_taskgroup_children_have_dotted_ordinals() -> None:
    """Children of a top-level taskgroup must have ordinals '1.1' and '1.2'."""

    yaml_lines = [
        "name: nested-children",
        "flow:",
        "  - taskgroup: outer-group",
        "    items:",
        "      - task: child-a",
        "        tasktype: {0}".format(_GIT_TASKTYPE),
        "      - task: child-b",
        "        tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    group_node = workflow.flow[0]
    child_items = group_node.items

    verification.assert_equal(len(child_items), 2)
    verification.assert_equal(child_items[0].ordinal, "1.1")
    verification.assert_equal(child_items[1].ordinal, "1.2")
    verification.assert_true(isinstance(child_items[0], Task))
    verification.assert_true(isinstance(child_items[1], Task))
    return


def test_parse_deeply_nested_taskgroup_produces_dotted_ordinal() -> None:
    """A deeply nested task must have an ordinal like '1.2.1'."""

    yaml_lines = [
        "name: deeply-nested",
        "flow:",
        "  - taskgroup: outer",
        "    items:",
        "      - task: head",
        "        tasktype: {0}".format(_GIT_TASKTYPE),
        "      - taskgroup: inner",
        "        items:",
        "          - task: deep",
        "            tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    yaml_text = "\n".join(yaml_lines)
    stream = StringIO(yaml_text)

    workflow = Workflow.parse(workflow_stream=stream)

    outer_group = workflow.flow[0]
    inner_group = outer_group.items[1]
    deep_task = inner_group.items[0]

    verification.assert_equal(outer_group.ordinal, "1")
    verification.assert_equal(inner_group.ordinal, "1.2")
    verification.assert_equal(deep_task.ordinal, "1.2.1")
    verification.assert_equal(deep_task.label, "deep")
    return
