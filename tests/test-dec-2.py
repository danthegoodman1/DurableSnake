from __future__ import annotations
from typing import Callable, TypeVar, ParamSpec, cast, Any
from functools import wraps
import inspect
from contextvars import ContextVar

P = ParamSpec("P")
R = TypeVar("R")

# Context variable to track durable execution
execution_context: ContextVar[str | None] = ContextVar(
    "execution_context", default=None
)


def durable(fn: Callable[P, R]) -> Callable[P, R]:
    sig = inspect.signature(fn)

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Set context to indicate durable execution
        token = execution_context.set("durable")
        try:
            print(f"  [Context: {execution_context.get()}] Executing {fn.__name__}")
            result = fn(*args, **kwargs)
            return result
        finally:
            execution_context.reset(token)

    cast(Any, wrapper).__signature__ = sig
    return wrapper


# Example:
@durable
def add_one(a: int) -> int:
    """adds one"""
    return a + 1


# Test runtime preservation of metadata
print("\n=== Testing decorated function ===")
result = add_one(2)
print(f"Result: {result}")
print(f"__doc__: {add_one.__doc__}")
print(f"__qualname__: {add_one.__qualname__}")
sig = inspect.signature(add_one)
print(f"signature: {sig}")
for name, param in sig.parameters.items():
    print(f"  {name}: {param.annotation}")
print(f"  return: {sig.return_annotation}")


# Test with non-decorated function for comparison
def add_two(a: int) -> int:
    """adds two"""
    print(f"  [Context: {execution_context.get()}] Inside add_two")
    return a + 2


print("\n=== Testing non-decorated function ===")
print(f"add_two(2): {add_two(2)}")
print(f"Current context after call: {execution_context.get()}")
