"""
.. module:: shellscript
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the EmbeddedPython task class which implements
               the execution of inline python based tasks in a workpacket.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

import os

from automojo.xmodules.xformatting import indent_lines

from automojo.taskplus.model.task import Task

class EmbeddedPython(Task):
    """
        A task class that is used to setup the running of an embedded python script
        in the context of the automation worker.
    """

    def __init__(self, ordinal: str, label: str, task_info: dict, logger):
        super(EmbeddedPython, self).__init__(ordinal, label, task_info, logger)
        self._script = task_info["script"]
        return

    @property
    def script(self) -> List[str]:
        return self._script

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:

        script_content = os.linesep.join(self._script)
        script_content = indent_lines(script_content, level=3)

        exit_status = 0

        try:
            # Execute the inline python script in the context of the current
            # globals and locals.
            exec(script_content, globals(), locals())
        except:
            exit_status = 1

        return exit_status
