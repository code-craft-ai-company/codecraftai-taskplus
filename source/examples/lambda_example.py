import inspect
import ast

class Workflow:
    def __init__(self, query_mode=True):
        self.query_mode = query_mode
        self.call_graph = []

    def choice(self):
        return Choice(self)

class Choice:
    def __init__(self, workflow):
        self.workflow = workflow

    def _capture_expression(self, func, activity):
        # 1. Inspect the caller's stack to get the source of the method call
        frame = inspect.currentframe().f_back.f_back
        source_line = inspect.getframeinfo(frame).code_context[0].strip()
        
        # 2. Parse the source into an Abstract Syntax Tree (AST)
        tree = ast.parse(source_line)
        
        # 3. Find the lambda node within the method call (if, elif)
        lambda_code = "Unknown"
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                # Turn the AST node back into a readable string
                lambda_code = ast.unparse(node)
                break
        
        # 4. Log the decision logic instead of executing it
        self.workflow.call_graph.append({
            "condition": lambda_code,
            "action": activity.__name__ if hasattr(activity, '__name__') else str(activity)
        })

    def if_(self, condition_lambda, activity):
        if self.workflow.query_mode:
            self._capture_expression(condition_lambda, activity)
        else:
            # Normal execution logic here
            pass

    def elif_(self, condition_lambda, activity):
        if self.workflow.query_mode:
            self._capture_expression(condition_lambda, activity)

# Example Usage
def some_activity(): pass
def other_activity(): pass

class SomeWorkflow:
    def run(self, flow: Workflow):
        choice = flow.choice()
        # Use if_ because 'if' is a reserved keyword in Python
        choice.if_(lambda x, y: x == y, some_activity)
        choice.elif_(lambda x, y: x > y, other_activity)

# Execution in Query Mode
flow_engine = Workflow(query_mode=True)
my_workflow = SomeWorkflow()
my_workflow.run(flow_engine)

# Output the captured call graph
for step in flow_engine.call_graph:
    print(f"Condition: {step['condition']} -> Action: {step['action']}")

    