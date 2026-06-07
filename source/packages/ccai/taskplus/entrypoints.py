"""
.. module:: entrypoints
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A set of standaridized entry point functions that provide standardized task orchestration
               of workpacket jobs.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2020, Myron W Walker"
__credits__ = []


import logging
import sys


from ccai.taskplus.model.flowengine import FlowEngine
from ccai.taskplus.model.workflow import Workflow


logger = logging.getLogger()


def run_workflow_entrypoint(workflow_file: str):
    """
        This is the entry point for the execution of workpackets.  It provides a the execution
        context for the execution of the orchestration steps in the workpacket.

        name: Example Workflow A
        environment:
            AKIT_BUILD_BRANCH: somebranch
            AKIT_BUILD_NAME: somebuild-2.1.456
            AKIT_JOBTYPE: unknown

        parameters:
            branch: somebranch
            build: somebuild-2.1.456
            landscape: $HOME/ccai/config/default-landscape.yaml

        tasklist:
            - task: Print OS Name
            tasktype: ccai.taskplus.tasks.embeddedpython@EmbeddedPython
            script:
                - import os
                - print(os.name)

            - task: List Directories
            tasktype: ccai.taskplus.tasks.shellscript@BashScript
            script:
                - ls -al

    """
    # We must exit with a result code, initialize it to 0 here
    result_code = 0

    workflow = None

    with open(workflow_file, 'r') as wpf:
        workflow = Workflow.parse(wpf)

    flowengine = FlowEngine()
    result_code = flowengine.execute(workflow)

    sys.exit(result_code)

    return
