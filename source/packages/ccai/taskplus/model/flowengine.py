
__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List

from ccai.taskplus.model.flownode import FlowNode
from ccai.taskplus.model.task import Task
from ccai.taskplus.model.taskgroup import TaskGroup
from ccai.taskplus.model.workflow import Workflow


class JumpContext:
    def __init__(self):
        self.seeking_node = None
        return


class FlowEngine:

    def __init__(self):
        return


    def evaluate_expression(self, if_expr: str, environment: Dict[str, str], parameters: Dict[str, Any], flowstate: Dict[str, Any]) -> bool:

        # ``flowstate`` is the per-run state threaded through ``process_flowitems``
        # and updated by each task; an ``if:`` expression is evaluated against it
        # (plus ``environment``/``parameters``) so conditional flow can reference
        # accumulated state. (Previously this read the always-empty instance
        # ``self._flowstate`` and was passed no per-run state at all.)
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
                include_node = self.evaluate_expression(fitem.if_expr, environment, parameters, flowstate)

            if include_node:
                if isinstance(fitem, Task):

                    task_result = fitem.execute(environment, parameters, flowstate)
                    if task_result != 0:
                        if fitem.onfailure is not None:
                            # The failure is routed to a handler node -- treat it
                            # as handled and let the handler decide the outcome.
                            jump_context.seeking_node = fitem.onfailure
                        else:
                            # An unhandled task failure must surface so that
                            # execute() returns a non-zero code (CI gating).
                            failure_info = {
                                "node": node_label,
                                "result_code": task_result,
                            }
                            errors.append(failure_info)
                    elif fitem.onsuccess is not None:
                        jump_context.seeking_node = fitem.onsuccess

                elif isinstance(fitem, TaskGroup):

                    group_items = fitem.items

                    self.process_flowitems(environment, parameters, flowstate, errors, group_items,
                                           jump_context)

        return

