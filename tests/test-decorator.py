import asyncio

from durable_snake.workflow import activity, workflow_execution_context


@activity("thing")
async def thing(hey: str, ho: str = None) -> int:
    print("thing:", hey, ho)
    return 2

async def fake_workflow():
    workflow_execution_context.set({"some": "data"})
    return await thing("yeye")

asyncio.run(thing("before"))
asyncio.run(fake_workflow())
asyncio.run(thing("after"))
c