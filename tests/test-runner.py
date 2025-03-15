from durable_snake.runner import Runner, RunnerOptions
import asyncio
from loguru import logger
import sys

logger.remove(0) # disable default logger
logger.add(sys.stdout, level="DEBUG") # set to debug


runner = Runner(options=RunnerOptions(id="runner1", queue="queue1", backend=None))

asyncio.run(runner.start())
