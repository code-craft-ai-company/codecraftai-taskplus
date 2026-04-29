

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []

from typing import Any, Dict, List


import logging


import os

from io import TextIOWrapper
from pprint import pformat

import yaml

from automojo.errors.exceptions import ConfigurationError

from automojo.xmodules.ximport import import_by_name
from automojo.xmodules.xformatting import indent_lines

from automojo.taskplus.model.flownode import FlowNode
from automojo.taskplus.model.task import Task
from automojo.taskplus.model.taskgroup import TaskGroup

logger = logging.getLogger()


class Workflow:

    def __init__(self, environment: Dict[str, str], parameters: Dict[str, Any], flow: List[FlowNode]):
        self._environment = environment
        self._parameters = parameters
        self._flow = flow
        return
    
    @property
    def environment(self) -> Dict[str, str]:
        return self._environment
    
    @property
    def flow(self) -> List[FlowNode]:
        return self._flow

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters

    @classmethod
    def parse(cls, workflow_stream: TextIOWrapper) -> "Workflow":

        workflow_info = yaml.safe_load(workflow_stream)

        environment = {}
        if "environment" in workflow_info:
            environment = workflow_info["environment"]

        parameters = {}
        if "parameters" in workflow_info:
            parameters = workflow_info["parameters"]

        if "name" not in workflow_info:
            errmsg = "A workflow document must have a 'name' element."
            raise ConfigurationError(errmsg)

        if "flow" not in workflow_info:
            errmsg = "A workflow document must have a 'flow' element which contains the tasks to be performed."
            raise ConfigurationError(errmsg)

        fnode_info_items = workflow_info["flow"]

        flow_items = cls._process_flow_info_items(fnode_info_items)

        workflow = Workflow(environment, parameters, flow_items)

        return workflow

    @classmethod
    def _process_flow_info_items(cls, fnode_info_items: List[Dict[str, Any]], ordinal_prefix: str="") -> List[FlowNode]:

        flow_items: List[FlowNode] = []

        ordinal_position = 0

        for fnode_info in fnode_info_items:

            ordinal_position += 1

            next_ordinal = str(ordinal_position)
            if len(ordinal_prefix) > 0:
                next_ordinal = f"{ordinal_prefix}.{str(ordinal_position)}"

            if "task" in fnode_info:
                task_label = fnode_info["task"]

                if "taskgroup" in fnode_info:
                    errmsg = "A 'task' node should not have a 'taskgroup' field."
                    raise ConfigurationError(errmsg)

                task_type = fnode_info["tasktype"]

                task_module_name, task_module_class = task_type.split("@")
                task_module = import_by_name(task_module_name)

                if hasattr(task_module, task_module_class):
                    task_class = getattr(task_module, task_module_class)

                    task_inst: Task = task_class(next_ordinal, task_label, fnode_info, logger)
                    flow_items.append(task_inst)
                else:
                    error_msg = "The specified task module %r does not contain a class %r" % (
                        task_module_name, task_module_class)
                    raise ConfigurationError(error_msg) from None

            elif "taskgroup" in fnode_info:

                tg_label = fnode_info["taskgroup"]

                if "items" not in fnode_info:
                    errmsg = "A 'taskgroup' node must have an 'items' field."
                    raise ConfigurationError(errmsg)

                tg_items_info_list = fnode_info["items"]

                tg_titems = cls._process_flow_info_items(tg_items_info_list, ordinal_prefix=next_ordinal)

                tgroup_inst = TaskGroup(next_ordinal, tg_label, fnode_info, tg_titems, logger)
                flow_items.append(tgroup_inst)

            else:
                errmsg_lines = [
                    "Unknown workflow node encountered."
                ]
                errmsg_lines.append(indent_lines(pformat(fnode_info, indent=4, depth=2), level=1))

                errmsg = os.linesep.join(errmsg_lines)
                raise ConfigurationError(errmsg)

        return flow_items