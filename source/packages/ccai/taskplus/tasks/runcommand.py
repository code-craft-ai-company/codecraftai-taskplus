"""
.. module:: runcommand
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the RunCommand task class which implements
               the execution of a singular command based tasks in a workpacket.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional

import os
import subprocess

from ccai.xmodules.xformatting import indent_lines

from ccai.taskplus.model.task import Task

class RunCommand(Task):

    def __init__(self, ordinal: str, label: str, task_info: dict, logger):
        super(RunCommand, self).__init__(ordinal, label, task_info, logger)
        self._command = task_info["command"]
        return

    @property
    def command(self) -> str:
        return self._command

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:

        self._logger.info("Running Command: %s" % self._command)

        proc = subprocess.Popen([self._command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()

        stdout = stdout.decode()
        stderr = stderr.decode()

        log_msg_lines = [
            "RESULT CODE: %d" % exit_code,
            "STDOUT:",
            indent_lines(stdout, level=1),
            "STDERR:",
            indent_lines(stderr, level=1),
        ]

        log_msg = os.linesep.join(log_msg_lines)
        if exit_code == 0:
            self._logger.info(log_msg)
        else:
            self._logger.error(log_msg)

        return exit_code