from enum import Enum
import inspect
from pydantic import BaseModel
import functools
from typing import Callable, TypeVar, cast

from .internal.contexts import _workflow_execution_context


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


F = TypeVar("F", bound=Callable)


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
    print("activity decorator")

    def decorator(func: F) -> F:
        nonlocal var_name
        if var_name is None:
            var_name = func.__name__

        # # Create context variable attached to the function
        # context_var = contextvars.ContextVar(var_name, default=default)
        #
        # # Attach the context variable to the function for easy access
        # setattr(func, 'context_var', context_var)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            print("params", *args, **kwargs)
            print("workflow context", _workflow_execution_context.get())
            result = func(*args, **kwargs)
            print("result", result)
            return result

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            print("params", *args, **kwargs)
            print("workflow context", _workflow_execution_context.get())
            result = await func(*args, **kwargs)
            print("result", result)
            return result

        # Choose the appropriate wrapper based on whether the function is a coroutine
        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator


T = TypeVar("T", bound=Callable)


def workflow(athing: str | None = None):
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
    print("workflow decorator")

    def decorator(func: T) -> T:
        is_async = inspect.iscoroutinefunction(func)

        class CallableActivity:
            # Copy function metadata
            __name__ = func.__name__
            __doc__ = func.__doc__
            __module__ = func.__module__
            __qualname__ = func.__qualname__
            __annotations__ = func.__annotations__

            def __call__(self, *args, **kwargs):
                print("params", *args, **kwargs)
                print("workflow context", _workflow_execution_context.get())

                if is_async:
                    # For async functions, return a coroutine
                    async def async_execution():
                        result = await func(*args, **kwargs)
                        print("result", result)
                        return result

                    return async_execution()
                else:
                    # For sync functions, execute directly
                    result = func(*args, **kwargs)
                    print("result", result)
                    return result

            # Add any additional methods here
            def get_athing(self):
                return athing

            # Add any other properties or methods

        # Create an instance and make it look like the original function
        callable_instance = CallableActivity()

        return cast(T, callable_instance)

    return decorator
