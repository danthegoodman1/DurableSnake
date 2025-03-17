import asyncio
from durable_snake.workflow import activity


@activity("im asycj")
async def test_decorator():
    print("im async")
    return "async"


@activity("im sync")
def test_decorator_sync():
    print("im sync")
    return "sync"


asyncio.run(test_decorator())
print()
print(test_decorator.get_athing())
print()
test_decorator_sync()
