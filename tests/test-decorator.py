import asyncio
from durable_snake.workflow import activity, workflow


@activity("im asycj")
async def test_decorator():
    print("im async")
    return "async"


@workflow("im sync")
def test_decorator_sync():
    print("im sync")
    return "sync"


asyncio.run(test_decorator())
print()
print(test_decorator_sync.get_athing())
print()
test_decorator_sync()
