"""Tests for the :class:`FlowNode` base class."""

from typing import Any, Dict

import logging

from ccai.testbase import verification

from ccai.taskplus.model.flownode import FlowNode


class _ConcreteFlowNode(FlowNode):
    """
        Minimal concrete subclass of :class:`FlowNode` used to exercise the
        non-abstract behavior of the base class in tests.
    """


def _make_logger() -> logging.Logger:
    rtnval = logging.getLogger("test")
    return rtnval


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_construct_stores_ordinal_label_node_info_and_logger() -> None:
    """Constructing a FlowNode stores the ordinal, label, and node_info."""

    logger = _make_logger()
    node_info: Dict[str, Any] = {"if": "True"}

    node = _ConcreteFlowNode(ordinal="0001", label="alpha", node_info=node_info, logger=logger)

    verification.assert_equal(node.ordinal, "0001")
    verification.assert_equal(node.label, "alpha")
    verification.assert_equal(node.node_info, node_info)
    return


def test_flownode_is_abc_subclass() -> None:
    """The :class:`FlowNode` base class is registered as an :mod:`abc` ABC."""

    import abc

    is_abc = issubclass(FlowNode, abc.ABC)

    verification.assert_equal(is_abc, True)
    return


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------


def test_ordinal_property_returns_constructed_value() -> None:
    """The :py:attr:`ordinal` property echoes the constructed value."""

    node = _ConcreteFlowNode(ordinal="0007", label="alpha", node_info={}, logger=_make_logger())

    ordinal_value = node.ordinal

    verification.assert_equal(ordinal_value, "0007")
    return


def test_label_property_returns_constructed_value() -> None:
    """The :py:attr:`label` property echoes the constructed value."""

    node = _ConcreteFlowNode(ordinal="0001", label="my-label", node_info={}, logger=_make_logger())

    label_value = node.label

    verification.assert_equal(label_value, "my-label")
    return


def test_node_info_property_returns_constructed_value() -> None:
    """The :py:attr:`node_info` property echoes the constructed dictionary."""

    node_info: Dict[str, Any] = {"if": "True", "onfailure": "rescue", "onsuccess": "next"}
    node = _ConcreteFlowNode(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    node_info_value = node.node_info

    verification.assert_equal(node_info_value, node_info)
    return


def test_node_info_property_returns_same_object_reference() -> None:
    """The :py:attr:`node_info` property returns the same dict instance passed in."""

    node_info: Dict[str, Any] = {"if": "True"}
    node = _ConcreteFlowNode(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    is_same_object = node.node_info is node_info

    verification.assert_equal(is_same_object, True)
    return


def test_if_expr_property_returns_value_when_key_present() -> None:
    """When ``node_info`` contains an ``if`` key, :py:attr:`if_expr` returns its value."""

    node_info: Dict[str, Any] = {"if": "result == 0"}
    node = _ConcreteFlowNode(ordinal="0001", label="alpha", node_info=node_info, logger=_make_logger())

    if_expr_value = node.if_expr

    verification.assert_equal(if_expr_value, "result == 0")
    return


def test_if_expr_property_returns_none_when_key_missing() -> None:
    """When ``node_info`` does not contain an ``if`` key, :py:attr:`if_expr` returns ``None``."""

    node = _ConcreteFlowNode(ordinal="0001", label="alpha", node_info={}, logger=_make_logger())

    if_expr_value = node.if_expr

    verification.assert_equal(if_expr_value, None)
    return
