"""
.. module:: initialize
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Helper routines used to initialize the TaskPlus runtime.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import os

from ccai.thisapp.persona import establish_app_persona
from ccai.thisapp.runtimevariables import resolve_runtime_variables


TASKPLUS_APP_NAME = "ccai"
TASKPLUS_LOGGER_NAME = "TaskPlus"
TASKPLUS_LOG_BASENAME = "workflow"


def initialize_taskplus_runtime():
    """
        Initializes the TaskPlus runtime by establishing the application persona and resolving the runtime
        variables, the same way the ``testbase`` and ``testplus`` commands initialize their runtimes.  The runtime
        must be initialized before runtime option overrides such as the output directory, start time or log levels
        can be applied.

        ..note: Both :func:`establish_app_persona` and :func:`resolve_runtime_variables` only take effect the first
                time they are called in a process, so when TaskPlus is running inside a process that has already
                initialized a runtime, such as a ``testbase`` test run, the existing runtime is used.
    """

    home_dir = os.path.join(os.path.expanduser("~"), TASKPLUS_APP_NAME)

    establish_app_persona(name=TASKPLUS_APP_NAME, presence_dir=home_dir, logger_name=TASKPLUS_LOGGER_NAME,
                          log_basename=TASKPLUS_LOG_BASENAME)

    resolve_runtime_variables()

    return
