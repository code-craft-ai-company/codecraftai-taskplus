from typing import Callable


class Activity:
    """
        Docstring for Activity
    """

class Branch:

    def if_(self, expression: Callable, activity: Activity):

        return
    
    def elif_(self, expression: Callable, activity: Activity):
        return
    
    def else_(self, expression: Callable, activity: Activity):
        return

class Switch:

    def case(self, expression: Callable, activity: Activity, fallthrough: bool = False):
        return

class Flow:

    def branch(self):
        return
    
    def switch(self):
        return
    
class Orchestrator:
    """
    Docstring for Orchestrator
    """


orchestrator = OrchestratorSingleton()


workflow = orchestrator.create_workflow(id="", name="SomeName")

@workflow.activity(entry=True)
class EntryActivity(Activity):

    def run(self, flow: Flow):

        return