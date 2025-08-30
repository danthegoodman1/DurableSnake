from __future__ import annotations
from typing import Callable, Protocol, TypeVar, ParamSpec, cast, Any
from functools import wraps
import inspect

P = ParamSpec("P")
R = TypeVar("R", covariant=True)


class DurableFunc(Protocol[P, R]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def durable(self, *args: P.args, **kwargs: P.kwargs) -> R: ...


def durable(fn: Callable[P, R]) -> DurableFunc[P, R]:
    sig = inspect.signature(fn)

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return fn(*args, **kwargs)

    cast(Any, wrapper).__signature__ = sig

    @wraps(fn)
    def run_durable(*args: P.args, **kwargs: P.kwargs) -> R:
        # Insert durable-execution logic here; fallback to direct call
        return fn(*args, **kwargs)

    cast(Any, run_durable).__signature__ = sig

    setattr(wrapper, "durable", run_durable)
    return cast(DurableFunc[P, R], wrapper)


# Example:
@durable
def add_one(a: int) -> int:
    """adds one"""
    return a + 1


# Test runtime preservation of metadata
print("add_one(2):", add_one(2))
print("  __doc__:", add_one.__doc__)
print("  __qualname__:", add_one.__qualname__)
sig = inspect.signature(add_one)
print("  signature:", sig)
for name, param in sig.parameters.items():
    print(f"    {name}: {param.annotation}")
print(f"    return: {sig.return_annotation}")

print("\nadd_one.durable(2):", add_one.durable(2))
print("  __doc__:", add_one.durable.__doc__)
print("  __qualname__:", add_one.durable.__qualname__)
sig_durable = inspect.signature(add_one.durable)
print("  signature:", sig_durable)
for name, param in sig_durable.parameters.items():
    print(f"    {name}: {param.annotation}")
print(f"    return: {sig_durable.return_annotation}")
