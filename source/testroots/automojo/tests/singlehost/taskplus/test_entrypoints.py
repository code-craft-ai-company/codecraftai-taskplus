"""
    Tests for :mod:`automojo.taskplus.entrypoints`, which exposes the
    ``run_workflow_entrypoint`` function used by the Click CLI.

    ``run_workflow_entrypoint`` always terminates with ``sys.exit``, so
    each happy-path test catches :class:`SystemExit` and inspects the
    ``code`` attribute.
"""

import os
import tempfile

from automojo.testbase import verification

from automojo.taskplus.entrypoints import run_workflow_entrypoint


_GIT_TASKTYPE = "automojo.taskplus.tasks.gitcheckout@GitCheckout"


def _write_temp_yaml(yaml_text: str) -> str:
    """
        Write ``yaml_text`` to a freshly-created temp ``.yaml`` file and
        return its absolute path.

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


def _empty_flow_yaml() -> str:
    """
        Build a YAML doc with the required ``name`` element and an empty
        ``flow`` list.

        :returns: The YAML document text.
    """

    yaml_lines = [
        "name: empty-workflow",
        "flow: []",
    ]
    rtnval = "\n".join(yaml_lines)
    return rtnval


def _single_task_yaml() -> str:
    """
        Build a YAML doc with a single GitCheckout task.

        :returns: The YAML document text.
    """

    yaml_lines = [
        "name: one-task-workflow",
        "flow:",
        "  - task: demo",
        "    tasktype: {0}".format(_GIT_TASKTYPE),
    ]
    rtnval = "\n".join(yaml_lines)
    return rtnval


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_run_workflow_entrypoint_with_empty_flow_exits_zero() -> None:
    """A workflow with an empty flow exits with code 0 via SystemExit."""

    workflow_path = _write_temp_yaml(_empty_flow_yaml())

    raised_system_exit = False
    exit_code = None
    try:
        try:
            run_workflow_entrypoint(workflow_path)
        except SystemExit as sysexit:
            raised_system_exit = True
            exit_code = sysexit.code
    finally:
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)

    verification.assert_equal(raised_system_exit, True)
    verification.assert_equal(exit_code, 0)
    return


def test_run_workflow_entrypoint_with_single_task_exits_zero() -> None:
    """A workflow with one GitCheckout task exits with code 0 via SystemExit."""

    workflow_path = _write_temp_yaml(_single_task_yaml())

    raised_system_exit = False
    exit_code = None
    try:
        try:
            run_workflow_entrypoint(workflow_path)
        except SystemExit as sysexit:
            raised_system_exit = True
            exit_code = sysexit.code
    finally:
        if os.path.exists(workflow_path):
            os.unlink(workflow_path)

    verification.assert_equal(raised_system_exit, True)
    verification.assert_equal(exit_code, 0)
    return


# ---------------------------------------------------------------------------
# Failure paths
# ---------------------------------------------------------------------------


def test_run_workflow_entrypoint_with_missing_file_raises_file_not_found() -> None:
    """An entrypoint pointed at a non-existent file raises FileNotFoundError."""

    bogus_path = os.path.join(
        tempfile.gettempdir(), "automojo-taskplus-no-such-workflow-xyz123.yaml"
    )

    if os.path.exists(bogus_path):
        os.unlink(bogus_path)

    raised = False
    try:
        run_workflow_entrypoint(bogus_path)
    except FileNotFoundError:
        raised = True

    verification.assert_equal(raised, True)
    return
