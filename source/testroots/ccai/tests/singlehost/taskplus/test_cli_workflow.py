"""
    Tests for the Click-based CLI in
    :mod:`ccai.taskplus.cli.cmdtree.workflow`.

    These exercise the ``command_taskplus_workflow_run`` command using
    Click's :class:`CliRunner`.  Click captures :class:`SystemExit` raised
    by the underlying ``run_workflow_entrypoint`` and surfaces it via the
    runner's ``result.exit_code``.

    The option tests patch the runtime initialization, the runtime option
    overrides, the job profile activation and the workflow entrypoint so
    they can verify how the ``run`` options are applied without changing
    the runtime of the process that is running the tests.
"""

from typing import Any, Dict, List, Optional, Tuple

import os
import tempfile

from datetime import datetime
from unittest import mock

from click.testing import CliRunner, Result

from ccai.testbase import verification

from ccai.runtime.optionoverrides import AM_RUNTIME_OPTION_OVERRIDES
from ccai.thisapp import activation
from ccai.thisapp.enumerations import ActivationProfile, JobType
from ccai.thisapp.runtimevariables import RuntimeVariables

from ccai.taskplus import entrypoints
from ccai.taskplus import initialize
from ccai.taskplus.cli.cmdtree.workflow import command_taskplus_workflow_run, parse_start_option


_GIT_TASKTYPE = "ccai.taskplus.tasks.gitcheckout@GitCheckout"


def _write_temp_yaml(yaml_text: str) -> str:
    """
        Write ``yaml_text`` to a fresh temp ``.yaml`` file.

        :param yaml_text: The YAML content to write.

        :returns: The absolute path to the file.
    """

    tmp = tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w"
    )
    try:
        tmp.write(yaml_text)
    finally:
        tmp.close()

    rtnval = tmp.name
    return rtnval


def _single_task_yaml() -> str:
    """
        Build a YAML doc with a single GitCheckout task.

        :returns: The YAML document text.
    """

    yaml_lines = [
        "name: cli-one-task",
        "flow:",
        "  - task: demo",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    rtnval = "\n".join(yaml_lines)
    return rtnval


# ---------------------------------------------------------------------------
# Failure cases
# ---------------------------------------------------------------------------


def test_cli_run_with_missing_file_argument_exits_nonzero() -> None:
    """
        Invoking ``run`` with a path that does not exist must result in a
        non-zero exit code (Click's :class:`BadParameter` handling).
    """

    runner = CliRunner()

    bogus_path = os.path.join(
        tempfile.gettempdir(),
        "codecraftai-taskplus-cli-no-such-workflow-zzz999.yaml",
    )
    if os.path.exists(bogus_path):
        os.unlink(bogus_path)

    result = runner.invoke(command_taskplus_workflow_run, [bogus_path])

    exit_code = result.exit_code
    is_nonzero = exit_code != 0

    verification.assert_equal(is_nonzero, True)
    return


def test_cli_run_with_empty_yaml_exits_nonzero() -> None:
    """
        A YAML file containing only whitespace causes ``yaml.safe_load`` to
        return ``None``, which the CLI converts into a :class:`BadParameter`
        and Click exits with a non-zero code.
    """

    workflow_path = _write_temp_yaml("\n")

    runner = CliRunner()

    try:
        result = runner.invoke(command_taskplus_workflow_run, [workflow_path])
    finally:
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)

    exit_code = result.exit_code
    is_nonzero = exit_code != 0

    verification.assert_equal(is_nonzero, True)
    return


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_cli_run_with_valid_yaml_exits_zero() -> None:
    """
        A valid YAML workflow should run through to completion.  The
        underlying ``run_workflow_entrypoint`` calls ``sys.exit(0)``, which
        Click's runner surfaces as ``result.exit_code == 0``.
    """

    workflow_path = _write_temp_yaml(_single_task_yaml())

    runner = CliRunner()

    try:
        result = runner.invoke(command_taskplus_workflow_run, [workflow_path])
    finally:
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)

    exit_code = result.exit_code

    verification.assert_equal(exit_code, 0)
    return


# ---------------------------------------------------------------------------
# Option handling
# ---------------------------------------------------------------------------


OVERRIDE_METHOD_NAMES = [
    "override_loglevel_console",
    "override_loglevel_file",
    "override_output_directory",
    "override_starttime",
]


def _invoke_run_with_patched_runtime(option_args: List[str], activation_profile: Optional[Any]) -> Tuple[Result, Dict[str, mock.MagicMock]]:
    """
        Invoke ``run`` for a valid workflow with the runtime initialization, the runtime
        option overrides, the job profile activation and the workflow entrypoint patched.

        :param option_args: The options to pass to ``run`` ahead of the workflow argument.
        :param activation_profile: The value ``RuntimeVariables.AM_ACTIVATION_PROFILE`` reports.

        :returns: The Click result and a dictionary of the mocks, keyed by the patched name,
                  with a ``manager`` mock that records the order of the calls.
    """

    workflow_path = _write_temp_yaml(_single_task_yaml())

    manager = mock.MagicMock()
    mocks = {"manager": manager}

    runner = CliRunner()

    try:
        with mock.patch.object(RuntimeVariables, "AM_ACTIVATION_PROFILE", activation_profile), \
             mock.patch.object(initialize, "initialize_taskplus_runtime") as mock_initialize, \
             mock.patch.object(AM_RUNTIME_OPTION_OVERRIDES, "override_loglevel_console") as mock_console, \
             mock.patch.object(AM_RUNTIME_OPTION_OVERRIDES, "override_loglevel_file") as mock_file, \
             mock.patch.object(AM_RUNTIME_OPTION_OVERRIDES, "override_output_directory") as mock_output, \
             mock.patch.object(AM_RUNTIME_OPTION_OVERRIDES, "override_starttime") as mock_start, \
             mock.patch.object(activation, "activate_profile_job") as mock_activate, \
             mock.patch.object(entrypoints, "run_workflow_entrypoint") as mock_entrypoint:

            manager.attach_mock(mock_initialize, "initialize_taskplus_runtime")
            manager.attach_mock(mock_console, "override_loglevel_console")
            manager.attach_mock(mock_file, "override_loglevel_file")
            manager.attach_mock(mock_output, "override_output_directory")
            manager.attach_mock(mock_start, "override_starttime")
            manager.attach_mock(mock_activate, "activate_profile_job")
            manager.attach_mock(mock_entrypoint, "run_workflow_entrypoint")

            mocks["initialize_taskplus_runtime"] = mock_initialize
            mocks["override_loglevel_console"] = mock_console
            mocks["override_loglevel_file"] = mock_file
            mocks["override_output_directory"] = mock_output
            mocks["override_starttime"] = mock_start
            mocks["activate_profile_job"] = mock_activate
            mocks["run_workflow_entrypoint"] = mock_entrypoint

            cli_args = list(option_args)
            cli_args.append(workflow_path)

            result = runner.invoke(command_taskplus_workflow_run, cli_args)
    finally:
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)

    return result, mocks


def test_cli_run_applies_output_option() -> None:
    """
        The ``--output`` option is applied as the output directory runtime override.
    """

    output_dir = os.path.join(tempfile.gettempdir(), "taskplus-cli-output")

    result, mocks = _invoke_run_with_patched_runtime(["--output", output_dir], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    mock_output = mocks["override_output_directory"]
    verification.assert_equal(mock_output.call_args_list, [mock.call(output_dir)])
    return


def test_cli_run_applies_start_option_as_datetime() -> None:
    """
        The ``--start`` option is parsed into a :class:`datetime` and applied as the
        start time runtime override.
    """

    result, mocks = _invoke_run_with_patched_runtime(["--start", "2020-10-17T15:30:11.989120"], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    expected_start = datetime(2020, 10, 17, 15, 30, 11, 989120)

    mock_start = mocks["override_starttime"]
    verification.assert_equal(mock_start.call_args_list, [mock.call(expected_start)])
    return


def test_cli_run_with_invalid_start_exits_nonzero() -> None:
    """
        An unparsable ``--start`` value is rejected before the runtime is changed or
        the workflow is run.
    """

    result, mocks = _invoke_run_with_patched_runtime(["--start", "not-a-timestamp"], ActivationProfile.Job)

    exit_code = result.exit_code
    is_nonzero = exit_code != 0
    verification.assert_equal(is_nonzero, True)

    mock_start = mocks["override_starttime"]
    verification.assert_equal(mock_start.called, False)

    mock_entrypoint = mocks["run_workflow_entrypoint"]
    verification.assert_equal(mock_entrypoint.called, False)
    return


def test_cli_run_applies_console_level_option() -> None:
    """
        The ``--console-level`` option is applied as the console log level runtime override.
    """

    result, mocks = _invoke_run_with_patched_runtime(["--console-level", "DEBUG"], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    mock_console = mocks["override_loglevel_console"]
    verification.assert_equal(mock_console.call_args_list, [mock.call("DEBUG")])
    return


def test_cli_run_applies_logfile_level_option() -> None:
    """
        The ``--logfile-level`` option is applied as the logfile log level runtime override.
    """

    result, mocks = _invoke_run_with_patched_runtime(["--logfile-level", "WARNING"], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    mock_file = mocks["override_loglevel_file"]
    verification.assert_equal(mock_file.call_args_list, [mock.call("WARNING")])
    return


def test_cli_run_without_options_applies_no_overrides() -> None:
    """
        When no options are passed, none of the runtime option overrides are applied.
    """

    result, mocks = _invoke_run_with_patched_runtime([], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    for method_name in OVERRIDE_METHOD_NAMES:
        override_mock = mocks[method_name]
        verification.assert_equal(override_mock.called, False)

    mock_entrypoint = mocks["run_workflow_entrypoint"]
    verification.assert_equal(mock_entrypoint.call_count, 1)
    return


def test_cli_run_activates_orchestration_profile_after_overrides() -> None:
    """
        When no profile has been activated, the runtime is initialized, the option overrides
        are applied, and then the 'Orchestration' job profile is activated before the
        workflow is run.
    """

    output_dir = os.path.join(tempfile.gettempdir(), "taskplus-cli-output")
    option_args = ["--output", output_dir, "--console-level", "INFO"]

    result, mocks = _invoke_run_with_patched_runtime(option_args, None)

    verification.assert_equal(result.exit_code, 0)

    manager = mocks["manager"]
    call_names = [call_item[0] for call_item in manager.mock_calls]
    expected_names = [
        "initialize_taskplus_runtime",
        "override_loglevel_console",
        "override_output_directory",
        "activate_profile_job",
        "run_workflow_entrypoint",
    ]
    verification.assert_equal(call_names, expected_names)

    mock_activate = mocks["activate_profile_job"]
    verification.assert_equal(mock_activate.call_args_list, [mock.call(job_type=JobType.Orchestration)])
    return


def test_cli_run_keeps_active_profile() -> None:
    """
        When a profile has already been activated in the process, the job profile is not
        activated a second time.
    """

    result, mocks = _invoke_run_with_patched_runtime([], ActivationProfile.Job)

    verification.assert_equal(result.exit_code, 0)

    mock_activate = mocks["activate_profile_job"]
    verification.assert_equal(mock_activate.called, False)
    return


def test_parse_start_option_accepts_filesystem_format() -> None:
    """
        The ``--start`` value may also use the filesystem safe time stamp format.
    """

    starttime = parse_start_option("2020-10-17T153011.989120")

    expected_start = datetime(2020, 10, 17, 15, 30, 11, 989120)
    verification.assert_equal(starttime, expected_start)
    return
