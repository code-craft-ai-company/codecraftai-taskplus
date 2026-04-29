=========================
Automation Mojo TaskPlus
=========================

The ``automojo-taskplus`` package provides support for integration-level orchestration. This level of automation and orchestration is used to orchestrate jobs running in a continuous integration system.

Highlights
==========

- Task and job model under ``taskplus/tasks/`` and ``taskplus/model/``.
- CLI command tree under ``taskplus/cli/cmdtree/`` for operator-driven task management.
- Examples demonstrating integration with continuous integration workflows.
- Designed to plug into the broader automojo suite for orchestrating CI-level jobs.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/testroots/automojo/`` - TestBase test roots.
- ``source/examples/`` - Example usage scripts.
- ``source/sphinx/`` - Sphinx documentation sources.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-envrionment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the single-host test suite:

.. code-block:: bash

   testbase testing run --root source/testroots/automojo --includes=automojo.tests.singlehost.taskplus --output=./.output

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
