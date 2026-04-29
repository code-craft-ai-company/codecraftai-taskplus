"""Tests for the :class:`TaskGroup` base class."""

from typing import Any, Dict, List

import logging

from automojo.testbase import verification

from automojo.taskplus.model.flownode import FlowNode
from automojo.taskplus.model.taskgroup import TaskGroup


class _ConcreteFlowNode(FlowNode):
    """Minimal concrete :class:`FlowNode` used as a child item in test groups."""


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


def _make_child_node(ordinal: str = "0001", label: str = "child") -> _ConcreteFlowNode:
    rtnval = _ConcreteFlowNode(ordinal=ordinal, label=label, node_info={}, logger=_make_logger())
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_with_empty_items_succeeds() -> None:
    """A :class:`TaskGroup` can be constructed with an empty items list."""

    group = TaskGroup(ordinal="0001", label="grp", node_info={}, items=[], logger=_make_logger())

    verification.assert_true(group is not None)
    return


def test_construct_stores_inherited_flownode_fields() -> None:
    """Constructing a TaskGroup initializes the inherited FlowNode fields."""

    node_info: Dict[str, Any] = {"if": "True"}
    group = TaskGroup(ordinal="0001", label="grp", node_info=node_info, items=[], logger=_make_logger())

    verification.assert_equal(group.ordinal, "0001")
    verification.assert_equal(group.label, "grp")
    verification.assert_equal(group.node_info, node_info)
    verification.assert_equal(group.if_expr, "True")
    return


def test_taskgroup_is_a_flownode() -> None:
    """A :class:`TaskGroup` instance is also a :class:`FlowNode`."""

    group = TaskGroup(ordinal="0001", label="grp", node_info={}, items=[], logger=_make_logger())

    is_flownode = isinstance(group, FlowNode)

    verification.assert_equal(is_flownode, True)
    return


# ---------------------------------------------------------------------------
# items property
# ---------------------------------------------------------------------------


def test_items_property_returns_empty_list_when_constructed_empty() -> None:
    """The :py:attr:`items` property returns an empty list when constructed empty."""

    group = TaskGroup(ordinal="0001", label="grp", node_info={}, items=[], logger=_make_logger())

    items_value = group.items

    verification.assert_equal(len(items_value), 0)
    return


def test_items_property_returns_constructed_list() -> None:
    """The :py:attr:`items` property returns the list of child FlowNodes passed in."""

    child_a = _make_child_node(ordinal="0001", label="a")
    child_b = _make_child_node(ordinal="0002", label="b")
    items: List[FlowNode] = [child_a, child_b]

    group = TaskGroup(ordinal="0010", label="grp", node_info={}, items=items, logger=_make_logger())

    items_value = group.items

    verification.assert_equal(len(items_value), 2)
    return


def test_items_property_preserves_order() -> None:
    """The :py:attr:`items` property preserves the order of the provided list."""

    child_a = _make_child_node(ordinal="0001", label="a")
    child_b = _make_child_node(ordinal="0002", label="b")
    items: List[FlowNode] = [child_a, child_b]

    group = TaskGroup(ordinal="0010", label="grp", node_info={}, items=items, logger=_make_logger())

    items_value = group.items
    first_label = items_value[0].label
    second_label = items_value[1].label

    verification.assert_equal(first_label, "a")
    verification.assert_equal(second_label, "b")
    return


def test_items_property_returns_same_list_reference() -> None:
    """The :py:attr:`items` property returns the same list object passed to the constructor."""

    items: List[FlowNode] = [_make_child_node()]
    group = TaskGroup(ordinal="0010", label="grp", node_info={}, items=items, logger=_make_logger())

    is_same_object = group.items is items

    verification.assert_equal(is_same_object, True)
    return
