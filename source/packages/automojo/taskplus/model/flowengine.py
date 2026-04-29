
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.errors.exceptions import ConfigurationError

from automojo.taskplus.model.flownode import FlowNode
from automojo.taskplus.model.task import Task
from automojo.taskplus.model.taskgroup import TaskGroup
from automojo.taskplus.model.workflow import Workflow


class JumpContext:
    def __init__(self):
        self.seeking_node = None
        return


class FlowEngine:

    def __init__(self):
        self._flowstate = {}
        return


    def evaluate_expression(self, if_expr: str, environment: Dict[str, str], parameters: Dict[str, Any]) -> bool:

        flowstate = self._flowstate

        eval_result = eval(if_expr)

        return eval_result


    def execute(self, workflow: Workflow) -> int:

        result_code = 0

        environment = workflow.environment
        parameters = workflow.parameters

        flowitems = workflow.flow

        flowstate = {}
        errors = []
        jump_context = JumpContext()

        self.process_flowitems(environment, parameters, flowstate, errors, flowitems, jump_context)

        if len(errors) > 0:
            result_code = 1

        return result_code


    def process_flowitems(self, environment: Dict[str, str], parameters: Dict[str, Any], flowstate: Dict[str, Any], errors: List,
                        flowitems: List[FlowNode], jump_context: JumpContext):

        for fitem in flowitems:

            node_label = fitem.label

            # If we are seeking a specific node, skip any nodes that are not that node
            if jump_context.seeking_node is not None:
                if jump_context.seeking_node != node_label:
                    continue
                else:
                    jump_context.seeking_node = None

            include_node = True
            if fitem.if_expr is not None:
                include_node = self.evaluate_expression(fitem.if_expr, environment, parameters)

            if include_node:
                if isinstance(fitem, Task):

                    task_result = fitem.execute(environment, parameters, flowstate)
                    if task_result != 0:
                        if fitem.onfailure is not None:
                            jump_context.seeking_node = fitem.onfailure
                    elif fitem.onsuccess is not None:
                        jump_context.seeking_node = fitem.onsuccess

                elif isinstance(fitem, TaskGroup):

                    group_items = fitem.items

                    self.process_flowitems(environment, parameters, flowstate, errors, group_items,
                                           jump_context)

        return

