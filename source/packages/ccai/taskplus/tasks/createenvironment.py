"""
.. module:: createenvironment
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the CreateEnvironment task class which implements
               the execution of environment creation commands.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, Optional

import os
import subprocess

from ccai.taskplus.model.task import Task

class CreateEnvironment(Task):
    """
        A task class that is used to create environment variables that persist and
        are consumable over the entire workflow.
    """

    def __init__(self, ordinal: int, label: str, task_info: dict, logger):
        super(CreateEnvironment, self).__init__(ordinal, label, task_info, logger)
        self._variables = task_info["variables"]
        return

    @property
    def variables(self) -> Dict[str, str]:
        return self._variables

    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:

        status_code = 0

        for var_info in self._variables:
            var_name = var_info["name"]

            if "command" in var_info:
                var_command = var_info["command"]

                command_env = dict(os.environ)

                # If "VIRTUAL_ENV" is set then we are running in a virtual environment, run the shell command
                # with the same virtual environment active.  Activation is expressed through the environment
                # of the child process (what an 'activate' script does) rather than a POSIX wrapper script, so
                # it works with both 'bin' (POSIX) and 'Scripts' (Windows) virtual environment layouts.
                if "VIRTUAL_ENV" in os.environ:
                    virtual_env = os.environ["VIRTUAL_ENV"]

                    if os.name == "nt":
                        virtual_env_bin = os.path.join(virtual_env, 'Scripts')
                    else:
                        virtual_env_bin = os.path.join(virtual_env, 'bin')

                    command_env["VIRTUAL_ENV"] = virtual_env
                    command_env["PATH"] = os.pathsep.join([virtual_env_bin, os.environ.get("PATH", "")])
                    if "PYTHONHOME" in command_env:
                        del command_env["PYTHONHOME"]

                # The command is a shell line, so it must be handed to the shell as a single string.  Wrapping it
                # in a list makes Windows re-quote the whole line into one token that is not recognized.
                proc = subprocess.Popen(var_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=command_env)
                stdout, stderr = proc.communicate()
                exit_code = proc.wait()

                if exit_code == 0:
                    var_val = stdout.decode().strip()
                    os.environ[var_name] = var_val
                else:
                    stderr_text = stderr.decode()
                    errmsg_lines = [
                        "Error creating environment variable '{}' with:".format(var_name),
                        "COMMAND: {}".format(var_command),
                        "STDERR: {}".format(stderr_text)
                    ]
                    errmsg = os.linesep.join(errmsg_lines)
                    self._logger.error(errmsg)
                    status_code = 1
            elif "value" in var_info:
                var_val = os.path.expandvars(os.path.expanduser(var_info["value"]))
                os.environ[var_name] = var_val
            else:
                errmsg_lines = [
                    "Error creating environment variable '{}': neither 'command' nor 'value' was specified.".format(var_name)
                ]
                errmsg = os.linesep.join(errmsg_lines)
                self._logger.error(errmsg)
                status_code = 1

        return status_code
