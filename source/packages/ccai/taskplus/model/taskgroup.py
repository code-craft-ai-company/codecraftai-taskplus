
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List


from logging import Logger


from ccai.taskplus.model.flownode import FlowNode


class TaskGroup(FlowNode):

    def __init__(self, ordinal: str, label: str, node_info: Dict[str, Any], items: List[FlowNode], logger: Logger):
        super().__init__(ordinal, label, node_info, logger)

        self._items = items
        return

    @property
    def items(self) -> List[FlowNode]:
        return self._items

