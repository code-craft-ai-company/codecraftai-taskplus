"""
    Tests for the Click-based CLI in
    :mod:`automojo.taskplus.cli.cmdtree.workflow`.

    These exercise the ``command_taskplus_workflow_run`` command using
    Click's :class:`CliRunner`.  Click captures :class:`SystemExit` raised
    by the underlying ``run_workflow_entrypoint`` and surfaces it via the
    runner's ``result.exit_code``.
"""

import os
import tempfile

from click.testing import CliRunner

from automojo.testbase import verification

from automojo.taskplus.cli.cmdtree.workflow import command_taskplus_workflow_run


_GIT_TASKTYPE = "automojo.taskplus.tasks.gitcheckout@GitCheckout"


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
        "automojo-taskplus-cli-no-such-workflow-zzz999.yaml",
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
