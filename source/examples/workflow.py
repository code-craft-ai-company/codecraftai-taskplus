from typing import Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


class Application:
    """
        Represents an application that can register workflows.
    """

    def __init__(self) -> None:
        self._workflows: Dict[str, Type] = {}
        self._workflow_entries: Dict[str, Callable] = {}
        return

    @property
    def workflows(self) -> Dict[str, Type]:
        return self._workflows

    def workflow(self, id: str) -> "WorkflowRegistration":
        """
            Creates a workflow registration decorator.

            :param id: The workflow identifier.
            :returns: A workflow registration decorator instance.
        """
        return WorkflowRegistration(self, id)

    def _register_workflow(self, id: str, workflow_type: Type, entry: Optional[Callable]) -> None:
        if id in self._workflows and self._workflows[id] is not workflow_type:
            errmsg = "A workflow is already registered for id=%s" % id
            raise ValueError(errmsg)

        self._workflows[id] = workflow_type
        if entry is not None:
            self._workflow_entries[id] = entry
        return

    def get_entry(self, id: str) -> Optional[Callable]:
        return self._workflow_entries.get(id)


class WorkflowRegistration:
    """
        Represents a workflow registration decorator.
    """

    def __init__(self, app: Application, id: str) -> None:
        self._app = app
        self._id = id
        return

    def __call__(self, cls: Type[T]) -> Type[T]:
        setattr(cls, "_decor_id_", self._id)
        entry_method = self._find_entry_method(cls)
        if entry_method is not None:
            setattr(cls, "_entry_", entry_method)

        self._app._register_workflow(self._id, cls, entry_method)
        return cls

    def entry(self, func: Callable) -> Callable:
        setattr(func, "_workflow_entry_id", self._id)
        return func

    def _find_entry_method(self, workflow_type: Type) -> Optional[Callable]:
        entry_methods = []
        for method in workflow_type.__dict__.values():
            if getattr(method, "_workflow_entry_id", None) == self._id:
                entry_methods.append(method)

        if len(entry_methods) > 1:
            errmsg = "Multiple entry methods were marked for workflow id=%s" % self._id
            raise ValueError(errmsg)

        if len(entry_methods) == 1:
            return entry_methods[0]

        return None


app = Application()
some_workflow = app.workflow(id="D40FBC2F-F70D-42C8-9826-DC129EBC22CE")


@some_workflow
class SomeWorkflow:

    name: str = "Example Workflow A"

    environment: Dict[str, str] = {
        "AKIT_BUILD_BRANCH": "somebranch",
        "AKIT_BUILD_NAME": "somebuild-2.1.456",
        "AKIT_JOBTYPE": "unknown"
    }

    parameters = {
        "branch": "somebranch"
    }


    @some_workflow.entry
    def run(self) -> None:
        return




