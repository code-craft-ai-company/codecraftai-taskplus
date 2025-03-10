
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict

import abc

from logging import Logger



class FlowNode(abc.ABC):

    def __init__(self, ordinal: str, label: str, node_info: Dict[str, Any], logger: Logger):
        self._ordinal = ordinal
        self._label = label
        self._node_info = node_info
        self._logger = logger

        self._if_expr = node_info.get("if")  # Task should run only if another task succeeds
        return
    
    @property
    def if_expr(self) -> str:
        return self._if_expr

    @property
    def label(self) -> str:
        return self._label
    
    @property
    def node_info(self) -> dict:
        return self._node_info
    
    @property
    def ordinal(self) -> str:
        return self._ordinal
