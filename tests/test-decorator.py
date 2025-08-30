import asyncio
from durable_snake.workflow import activity, workflow
from loguru import logger
import sys


@activity("im asycj")
async def test_decorator():
    context_logger = logger.bind(ip="192.168.0.1", user="someone")
    context_logger.info("Contextualize your logger easily")
    context_logger.bind(user="someone_else").info("Inline binding of extra attribute")
    context_logger.info(
        "Use kwargs to add context during formatting: {user}", user="anybody"
    )
    logger.info("im async")
    return "async"


@workflow("im sync")
def test_decorator_sync():
    logger.info("im sync")
    return "sync"


def format_extra(record):
    extra_items = []
    for key, value in record["extra"].items():
        extra_items.append(f"{key}={value}")
    extra_str = " ".join(extra_items)
    return "{time} {level} {message} {extra_str}".format(
        time=record["time"],
        level=record["level"],
        message=record["message"],
        extra_str=extra_str,
    )


logger.remove(0)
logger.add(
    sys.stdout,
    serialize=True,
    # format="{time} {level} {message} {extra}",
    format=format_extra,
    level="DEBUG",
)

asyncio.run(test_decorator())
print()
print(test_decorator_sync.get_athing())
print()
test_decorator_sync()
