__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from typing import Optional

import os

from datetime import datetime

import click
import yaml

from ccai.xmodules.xdatetime import DATETIME_FORMAT_FILESYSTEM, DATETIME_FORMAT_TIMESTAMP, parse_datetime
from ccai.xmodules.xlogging.levels import LOG_LEVEL_NAMES

HELP_WORK = "The file containing the workpacket detail for performing a workflow orchestration."
HELP_OUTPUT = "The output directory where results and artifacts are collected."
HELP_START = r"A time stamp to associate with the start of the run. Example: 2020-10-17T15:30:11.989120  Bash: date +%Y-%m-%dT%H:%M:%S.%N"
HELP_CONSOLE_LOG_LEVEL = "The logging level for console output."
HELP_FILE_LOG_LEVEL = "The logging level for logfile output."

START_FORMATS = [DATETIME_FORMAT_TIMESTAMP, DATETIME_FORMAT_FILESYSTEM]


def parse_start_option(start: str) -> datetime:
    """
        Parses the value of the '--start' option into a :class:`datetime`.  The value is parsed with the same
        timestamp and filesystem formats that are used to resolve the 'AM_STARTTIME' runtime variable.

        :param start: The time stamp string passed to the '--start' option.

        :returns: The start time as a :class:`datetime`.
        :raises: click.BadParameter
    """

    starttime = None

    for start_format in START_FORMATS:
        try:
            starttime = parse_datetime(start, datetime_format=start_format)
            break
        except ValueError:
            continue

    if starttime is None:
        err_msg_lines = [
            "The '--start' option value is not a valid time stamp.",
            f"    VALUE: {start}",
            "EXPECTED FORMATS:",
        ]
        for start_format in START_FORMATS:
            err_msg_lines.append(f"    {start_format}")
        errmsg = os.linesep.join(err_msg_lines)
        raise click.BadParameter(errmsg, param_hint="'--start'")

    return starttime


@click.group("workflow", help="Contains commands that are used to work with or run workflow scripts.")
def group_taskplus_workflow():
    return

@click.command("run")
@click.argument("workflow", required=True)
@click.option("--output", "-o", required=False, help=HELP_OUTPUT)
@click.option("--start", default=None, required=False, help=HELP_START)
@click.option("--console-level", default=None, required=False, type=click.Choice(LOG_LEVEL_NAMES, case_sensitive=False), help=HELP_CONSOLE_LOG_LEVEL)
@click.option("--logfile-level", default=None, required=False, type=click.Choice(LOG_LEVEL_NAMES, case_sensitive=False), help=HELP_FILE_LOG_LEVEL)
def command_taskplus_workflow_run(workflow: str, output: Optional[str] = None, start: Optional[str] = None,
                                  console_level: Optional[str] = None, logfile_level: Optional[str] = None):
    """
        Runs a workflow file.  The '--output', '--start', '--console-level' and '--logfile-level' options are applied
        as runtime option overrides, the same way the 'testbase' and 'testplus' run commands apply them, before the
        'Orchestration' job profile is activated so the output directory, start time and log levels are in effect
        for the workflow run.

        :param workflow: The path of the workflow file to run.
        :param output: The output directory where results and artifacts are collected.
        :param start: A time stamp to associate with the start of the run.
        :param console_level: The logging level for console output.
        :param logfile_level: The logging level for logfile output.

        :raises: click.BadParameter
    """

    # pylint: disable=unused-import,import-outside-toplevel

    # We do the imports of the automation framework code inside the action functions because
    # we don't want to startup loggin and the processing of inputs and environment variables
    # until we have entered an action method.  Thats way we know how to setup the environment.
    from ccai.runtime.optionoverrides import AM_RUNTIME_OPTION_OVERRIDES

    from ccai.thisapp.activation import activate_profile_job
    from ccai.thisapp.enumerations import JobType
    from ccai.thisapp.runtimevariables import RuntimeVariables

    from ccai.taskplus.initialize import initialize_taskplus_runtime

    workflow_file = os.path.abspath(os.path.expanduser(os.path.expandvars(workflow)))
    if not os.path.exists(workflow_file):
        error_msg = "The specified workflow file does not exist. file=%s" % workflow_file
        raise click.BadParameter(error_msg)

    # Validate the start time before we make any changes to the runtime.
    starttime = None
    if start is not None:
        starttime = parse_start_option(start)

    workflow_info = None
    with open(workflow_file, 'r') as wpf:
        wpfcontent = wpf.read()
        workflow_info = yaml.safe_load(wpfcontent)

    if workflow_info is not None:

        # STEP 1 - Initialize the runtime so the option overrides have a runtime to apply to.
        initialize_taskplus_runtime()

        # STEP 2 - Apply the runtime option overrides.  These must be applied before the job profile
        # is activated because the activation uses them to setup the output directory and logging.
        if console_level is not None:
            AM_RUNTIME_OPTION_OVERRIDES.override_loglevel_console(console_level)

        if logfile_level is not None:
            AM_RUNTIME_OPTION_OVERRIDES.override_loglevel_file(logfile_level)

        if output is not None:
            AM_RUNTIME_OPTION_OVERRIDES.override_output_directory(output)

        if starttime is not None:
            AM_RUNTIME_OPTION_OVERRIDES.override_starttime(starttime)

        # STEP 3 - Activate the 'Orchestration' job profile which sets up the output directory and logging.  A
        # profile can only be activated once per process, so when the workflow is run inside of a process that
        # has already activated a profile, such as a test run, the existing profile stays in effect.
        activation_profile = RuntimeVariables.AM_ACTIVATION_PROFILE
        if activation_profile is None:
            activate_profile_job(job_type=JobType.Orchestration)

        from ccai.taskplus.entrypoints import run_workflow_entrypoint

        # STEP 4 - Run the work packet
        run_workflow_entrypoint(workflow_file)

    else:
        error_msg = "Failure loading the work packet info from. file=%s" % workflow_file
        raise click.BadParameter(error_msg)

    return

group_taskplus_workflow.add_command(command_taskplus_workflow_run)
