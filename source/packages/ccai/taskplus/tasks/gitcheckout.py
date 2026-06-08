"""
.. module:: gitcheckout
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the ShellScript task class which implements
               the execution of shell based tasks in a workpacket.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional

from ccai.taskplus.model.task import Task

class GitCheckout(Task):

    def __init__(self, ordinal: str, label: str, task_info: dict, logger):
        super(GitCheckout, self).__init__(ordinal, label, task_info, logger)
        return

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:

        exit_code = 0
        return exit_code