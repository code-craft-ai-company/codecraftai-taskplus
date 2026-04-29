"""
.. module:: execution
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the function which implemented the execution workflow
               of an individual workpacket.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2020, Myron W Walker"
__credits__ = []


from typing import Any, Dict, List

import os

from automojo.xmodules.ximport import import_by_name

from automojo.errors.exceptions import ConfigurationError

from automojo.taskplus.model.task import Task


class JumpContext:
    def __init__(self) -> None:
        self.on_failure_section = None
        self.on_success_section = None


def execute_tasklist(logger, jump_context: JumpContext, parameters: dict, tasklist: List[Dict[str, Any]], ordinal_prefix: str=None, **kwargs):

    result_code = 0

    for index, item in enumerate(tasklist):
 
        nxt_ordinal = str(index)
        if ordinal_prefix is not None:
            nxt_ordinal = "{}.{}".format(ordinal_prefix, nxt_ordinal)

        if "task" in item:

            task_info: Dict[str, Any] = item

            task_label = task_info["task"]

            if jump_context.on_success_section is not None:
                if jump_context.on_success_section != task_label:
                    continue
                else:
                    jump_context.on_success_section = None

            if jump_context.on_failure_section is not None:
                if jump_context.on_failure_section != task_label:
                    continue
                else:
                    jump_context.on_failure_section = None

            task_type = item["tasktype"]

            task_module_name, task_module_class = task_type.split("@")
            task_module = import_by_name(task_module_name)

            if hasattr(task_module, task_module_class):
                task_class = getattr(task_module, task_module_class)

                task_instance: Task = task_class(nxt_ordinal, task_label, task_info, logger)

                task_result = task_instance.execute(parameters=parameters, **kwargs)
                if task_result != 0:
                    result_code = 1
                    if task_instance.onfailure is not None:
                        jump_context.on_failure_section = task_instance.onfailure
                elif task_instance.onsuccess is not None:
                    jump_context.on_success_section = task_instance.onsuccess

            else:
                error_msg = "The specified task module %r does not contain a class %r" % (
                    task_module_name, task_module_class)
                raise ConfigurationError(error_msg) from None

        elif "taskgroup" in item:

            tg_info: dict = item
            tg_label = tg_info["taskgroup"]

            if jump_context.on_success_section is not None:
                if jump_context.on_success_section != tg_label:
                    continue
                else:
                    jump_context.on_success_section = None

            if jump_context.on_failure_section is not None:
                if jump_context.on_failure_section != tg_label:
                    continue
                else:
                    jump_context.on_failure_section = None

            group_prefix = nxt_ordinal
            if ordinal_prefix is not None:
                nxt_ordinal = "{}.{}".format(ordinal_prefix, group_prefix)

            tg_items = tg_info["items"]

            tg_onfailure = tg_info.get("onfailure", None)
            tg_onsuccess = tg_info.get("onsuccess", None)

            tg_result = execute_tasklist(logger, jump_context, parameters, tg_items, ordinal_prefix=group_prefix)
            if tg_result != 0:
                result_code = 1
                if tg_onfailure is not None:
                    jump_context.on_failure_section = tg_onfailure
            elif tg_onsuccess is not None:
                jump_context.on_success_section = tg_onsuccess

        else:
            pass

    return result_code


def execute_workflow(logger, *, environment: dict, parameters: dict, workflow: list, **kwargs):

    # Publish the environment variables so they will take effect in the current
    # process and any sub-processes lauched from this process
    for key, val in environment.items():
        os.environ[key] = val

    jump_context = JumpContext()

    result_code = execute_tasklist(logger, jump_context, parameters, workflow)

    return result_code
