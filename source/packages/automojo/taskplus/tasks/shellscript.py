"""
.. module:: shellscript
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the ShellScript task class which implements
               the execution of shell based tasks in a workpacket.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []



from typing import Any, Dict, Optional

import os
import stat
import subprocess

from automojo.runtime.paths import get_temporary_file
from automojo.xmodules.xformatting import indent_lines

from automojo.taskplus.model.task import Task

class ShellScript(Task):

    def __init__(self, ordinal: str, label: str, task_info: dict, logger):
        super(ShellScript, self).__init__(ordinal, label, task_info, logger)
        self._script = task_info["script"]
        return

    @property
    def script(self) -> str:
        return self._script

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:

        script_content = os.linesep.join(self._script)

        tempfile = get_temporary_file(prefix="step-%s" % self._ordinal, suffix=".sh")

        self._logger.info("Running Script: %s" % tempfile)

        with open(tempfile, 'w') as tf:
            tf.write(script_content)

        os.chmod(tempfile, stat.S_IEXEC)

        proc = subprocess.Popen([tempfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()

        stdout_text = stdout.decode()
        stderr_text = stderr.decode()

        log_msg_script = [
            "RESULT CODE: %d" % exit_code,
            "STDOUT:",
            indent_lines(stdout_text, level=1),
            "STDERR:",
            indent_lines(stderr_text, level=1),
        ]

        log_msg = os.linesep.join(log_msg_script)
        if exit_code == 0:
            self._logger.info(log_msg)
        else:
            self._logger.error(log_msg)

        return exit_code