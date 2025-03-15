import contextvars
from enum import Enum
from pydantic import BaseModel
import functools
from typing import Callable, TypeVar, Any, Awaitable, cast


# TODO: update the type
workflow_execution_context = contextvars.ContextVar[dict | None]("workflow_execution", default=None)
task_execution_context = contextvars.ContextVar[dict | None]("task_execution", default=None)

class WorkflowStatus(Enum):
    # Open workflows
    PENDING = "pending"
    RUNNING = "running"

    # Closed workflows
    TERMINATED = "terminated"
    CONTINUED_AS_NEW = "continued_as_new"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class WorkflowInstance(BaseModel):
    """
    High level info about a workflow instance
    """

    id: str
    """The ID of the instance"""
    type: str
    """The type of workflow"""
    status: WorkflowStatus
    queue: str
    created_ns: int
    started_ns: int
    closed_ns: int
    parent_id: str | None = None
    data: dict | None = None

    # Updatable fields
    history_length: int = 0
    history_bytes: int = 0


T = TypeVar('T')

def workflow(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        print("Before function execution")

        # Call the original async function
        result = await func(*args, **kwargs)

        print("After function execution")

        return result

    return wrapper


F = TypeVar('F', bound=Callable)


def activity(var_name: str | None = None):
    """
    Decorate a function to be a workflow activity.

    Usage:
        @activity("request_id")
        async def process_request(request_id):
            # Access via context_var attribute on the function
            current_id = process_request.context_var.get()
            ...

        # Or with a value
        @activity("user", default="anonymous")
        def perform_operation():
            current_user = perform_operation.context_var.get()
            ...
    """

    def decorator(func: F) -> F:
        nonlocal var_name
        if var_name is None:
            var_name = func.__name__

        # # Create context variable attached to the function
        # context_var = contextvars.ContextVar(var_name, default=default)
        #
        # # Attach the context variable to the function for easy access
        # setattr(func, 'context_var', context_var)

        # @functools.wraps(func)
        # def sync_wrapper(*args, **kwargs):
        #     # For the first arg, use it to set the context if the name matches
        #     if args and var_name in func.__code__.co_varnames:
        #         token = context_var.set(args[0])
        #         try:
        #             return func(*args, **kwargs)
        #         finally:
        #             context_var.reset(token)
        #     else:
        #         return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            print("params", *args, **kwargs)
            print("workflow context", workflow_execution_context.get())
            result = await func(*args, **kwargs)
            print("result", result)
            return result

        # Choose the appropriate wrapper based on whether the function is a coroutine
        # if inspect.iscoroutinefunction(func):
        #     return cast(F, async_wrapper)
        # else:
        #     return cast(F, sync_wrapper)
        return cast(F, async_wrapper)

    return decorator
