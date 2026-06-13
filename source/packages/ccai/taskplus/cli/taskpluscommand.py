"""
    .. module:: taskpluscommand
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Defines the root ``taskplus`` command-line entry point and
               assembles the command tree.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Code Craft AI LLC"
__credits__ = []


import click

from ccai.taskplus.cli.cmdtree.workflow import group_taskplus_workflow


@click.group("taskplus", help="Code Craft AI TaskPlus workflow orchestration command-line interface.")
def taskplus_root_command():
    return


taskplus_root_command.add_command(group_taskplus_workflow)
