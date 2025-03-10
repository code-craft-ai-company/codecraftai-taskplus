"""
.. module:: taskbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: A module that provides the base task object that other tasks derive
               from.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2025, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional

import abc


from logging import Logger


from automojo.errors.exceptions import NotOverloadedError

from automojo.taskplus.model.flownode import FlowNode


class Task(FlowNode):

    def __init__(self, ordinal: str, label: str, node_info: Dict[str, Any], logger: Logger):
        super().__init__(ordinal, label, node_info, logger)

        self._onfailure = node_info.get("onfailure", None)
        self._onsuccess = node_info.get("onsuccess", None)

        return


    @property
    def onfailure(self) -> Optional[str]:
        return self._onfailure


    @property
    def onsuccess(self) -> Optional[str]:
        return self._onsuccess


    def execute(self, environment: Dict[str, str], parameters: Dict[str, Any], flowstate: Dict[str, Any]) -> int:

        self._logger.info("STEP: %s - %s" % (self._label, self._ordinal))

        result = self.perform_task(environment, parameters, flowstate)

        return result


    @abc.abstractmethod
    def perform_task(self, environment: Dict[str, str], parameters: Optional[Dict[str, Any]], flowstate: Dict[str, Any]) -> int:
        raise NotOverloadedError("TaskBase->execute must be overloaded by derived classes.") from None

