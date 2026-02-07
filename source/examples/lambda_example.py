import inspect
import ast
import abc
from typing import TypeVar, Generic, Type

T = TypeVar("T")



class Activity:
    def run(self, flow, **kwargs):
        raise NotImplementedError("run method must be implemented")

    @property
    def return_type(self):
        return None

    @property
    def return_schema(self):
        return None

    def query(self, flow, **kwargs):
        # Default behavior: return the schema if defined, otherwise None
        if self.return_type is dict and self.return_schema:
             return self.return_schema
        return self.return_type


    def __call__(self, flow, **kwargs):
        if isinstance(flow, WorkflowExecutor):
            return self.run(flow, **kwargs)
        else:
            return self.query(flow, **kwargs)


class Loop(abc.ABC):
    @abc.abstractmethod
    def __iter__(self):
        pass

    def query(self):
        yield

class While(Loop):
    def __init__(self, condition_lambda):
        self.condition_lambda = condition_lambda

    def __iter__(self):
        count = 0
        while self.condition_lambda():
            yield count
            count += 1

    def query(self):
        # In query mode, we execute the loop body once
        yield 0


class ItemInCollection(Loop, Generic[T]):
    def __init__(self, collection, item_type: Type[T]):
        self.collection = collection
        self.item_type = item_type

    def __iter__(self):
        for item in self.collection:
            yield item

    def query(self):
        # Yield the explicit item type
        yield self.item_type


class Workflow:

    def which(self):
        return Which(self)

    def choice(self):
        return Choice(self)

    def each(self, loop_iterator):
        raise NotImplementedError



class WorkflowExecutor(Workflow):
    
    def handle_condition(self, node, condition_lambda, activity, is_elif=False, is_else=False, **kwargs):
        if (is_elif or is_else) and node.matched:
            return

        # Execute condition
        if is_else or condition_lambda():
            activity(self, **kwargs)
            node.matched = True

    def handle_case(self, node, condition_lambda, activity, fallthrough=False, is_default=False, **kwargs):
        if node.falling_through or is_default or condition_lambda():
            activity(self, **kwargs)
            node.matched = True
            node.falling_through = fallthrough

        elif node.matched:
            # Already matched a previous case and didn't fall through
            pass

    def each(self, loop_iterator):
        yield from loop_iterator


class WorkflowQuery(Workflow):
    def __init__(self):
        self.call_graph = []

    def _capture_expression(self, func, activity, **kwargs):

        # 1. Inspect the caller's stack
        frame = inspect.currentframe().f_back.f_back.f_back # +1 for handle_... call
        source_line = inspect.getframeinfo(frame).code_context[0].strip()
        
        # 2. Parse AST
        tree = ast.parse(source_line)
        
        # 3. Find lambda
        lambda_code = "Unknown"
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                lambda_code = ast.unparse(node)
                break
        
        # 4. Log
        self.call_graph.append({
            "condition": lambda_code,
            "action": activity.__class__.__name__ if hasattr(activity, 'run') else (activity.__name__ if hasattr(activity, '__name__') else str(activity)),
            "parameters": kwargs
        })

    def handle_condition(self, node, condition_lambda, activity, is_elif=False, is_else=False, **kwargs):
        self._capture_expression(condition_lambda, activity, **kwargs)
        output_schema = activity(self, **kwargs)
        if output_schema:
            self.call_graph[-1]['outputs'] = output_schema

    def handle_case(self, node, condition_lambda, activity, fallthrough=False, is_default=False, **kwargs):
        if is_default:
           self._capture_expression(lambda: True, activity, **kwargs) # Placeholder for default
           # Hack: update last entry to say "Default"
           self.call_graph[-1]['condition'] = "Default"
        else:
           self._capture_expression(condition_lambda, activity, **kwargs)
        output_schema = activity(self, **kwargs)
        if output_schema:
            self.call_graph[-1]['outputs'] = output_schema

    def each(self, loop_iterator):
        condition_code = "Unknown"
        if hasattr(loop_iterator, 'condition_lambda'):
             # Attempt to capture the lambda source like before
             # For now, we reuse the existing _capture_expression logic if possible, 
             # but _capture_expression expects a function and stack inspection.
             # Since 'loop_iterator' is an object passed in, we might need to inspect *its* attributes
             # or just pass the lambda if available.
             self._capture_expression(loop_iterator.condition_lambda, "Each Start")
        else:
             self.call_graph.append({
                "condition": "Unknown Loop",
                "action": "Each Start"
             })

        yield from loop_iterator.query()
        
        self.call_graph.append({
            "condition": "End",
            "action": "Each End"
        })


class Branch:
    def __init__(self, workflow):
        self.workflow = workflow
        self.matched = False

class Which(Branch):
    def if_(self, condition_lambda, activity, **kwargs):
        self.workflow.handle_condition(self, condition_lambda, activity, is_elif=False, **kwargs)

    def elif_(self, condition_lambda, activity, **kwargs):
        self.workflow.handle_condition(self, condition_lambda, activity, is_elif=True, **kwargs)

    def else_(self, activity, **kwargs):
        self.workflow.handle_condition(self, lambda: True, activity, is_else=True, **kwargs)

class Choice(Branch):
    def __init__(self, workflow):
        super().__init__(workflow)
        self.falling_through = False

    def case_(self, condition_lambda, activity, fallthrough=False, **kwargs):
        self.workflow.handle_case(self, condition_lambda, activity, fallthrough, **kwargs)

    def default_(self, activity, **kwargs):
        self.workflow.handle_case(self, lambda: True, activity, is_default=True, **kwargs)



# Example Usage
class SomeActivity(Activity):
    @property
    def return_type(self):
        return dict

    @property
    def return_schema(self):
        return {"status": str, "id": int}

    def run(self, flow: Workflow, **kwargs):
        print(f"Running SomeActivity params={kwargs}")
        return {"status": "success", "id": 123}

class OtherActivity(Activity):
    @property
    def return_type(self):
        return dict

    @property
    def return_schema(self):
        return {"result": float}

    def run(self, flow: Workflow, **kwargs):
        print(f"Running OtherActivity params={kwargs}")
        return {"result": 0.0}


some_activity = SomeActivity()
other_activity = OtherActivity()

class SomeWorkflow:
    def run(self, flow: Workflow):

        # Example 1: Which (if/elif/else)
        which = flow.which()
        which.if_(lambda: 1 == 2, some_activity, message="First check") # False
        which.elif_(lambda: 2 > 3, other_activity, reason="Math is hard") # False (first elif)
        which.elif_(lambda: 1 == 1, some_activity, priority="High") # True (second elif)
        which.else_(other_activity, fallback=True) # Skipped


        # Example 2: Choice (switch/case/default)
        choice = flow.choice()
        choice.case_(lambda: 1 == 1, some_activity, case_id=1)
        choice.case_(lambda: 2 > 1, other_activity, fallthrough=True, speed="Fast")

        choice.default_(other_activity)

        # Example 3: Loop
        # Needs external state for execution mode loop
        self.counter = 0
        def loop_condition():
            self.counter += 1
            return self.counter <= 3

        # Using 'for i in flow.each()' if loop yields; or if loop is iterator
        for i in flow.each(While(loop_condition)):
           some_activity(flow, loop_index=i)

           inner_which = flow.which()
           inner_which.if_(lambda: self.counter % 2 == 0, some_activity)

        # Example 4: ItemInCollection
        items = ["apple", "banana", "cherry"]
        for item in flow.each(ItemInCollection(items, str)):
             # We can pass the item or properties of it to the activity
             some_activity(flow, item=item)




# Execution Mode
print("--- Execution Mode ---")
flow_executor = WorkflowExecutor()
my_workflow_exec = SomeWorkflow()
my_workflow_exec.run(flow_executor)

# Query Mode
print("\n--- Query Mode ---")
flow_query = WorkflowQuery()
my_workflow_query = SomeWorkflow()
my_workflow_query.run(flow_query)

# Output the captured call graph
for step in flow_query.call_graph:
    print(f"Condition: {step['condition']} -> Action: {step['action']} (Params: {step.get('parameters', {})}) => Outputs: {step.get('outputs', {})}")


    