from dataclasses import dataclass
from loguru import logger
from time import perf_counter_ns

from .backends import BaseBackend
from .workflow import WorkflowInstance
from .internal.contexts import _workflow_execution_context
from .internal import time_helpers
@dataclass
class RunnerOptions:
    id: str
    queue: str
    backend: BaseBackend

    expired_locks_poll_sec: float = 5.0
    step_concurrency: int = 0
    """Max number of steps that can be running at once. 0 means no limit"""
    pending_workflows_poll_sec: float = 2.0
    """How often to poll for pending workflows"""
    workflow_lock_expiration_sec: float = 10.0
    """How long to hold a workflow lock before attempting to extend it. The runner will attempt to extend the lock
    if it is within 1/2 of the expiration time."""

class Runner:
    """
    The workflow runner.
    """

    _workflows = {}
    _workflow_locks = {}

    def __init__(self, options: RunnerOptions):
        self._options = options
        logger.debug("Runner {} initialized", self._options.id)

    async def start(self):
        """
        Starts the runner
        """
        # Check for open locks that are owned by this runner
        held_locks = await self._options.backend.list_locks_held_by_runner(self._options.id)
        logger.trace("Found {} held locks", len(held_locks))
        # TODO: try to extend the locks
        for lock in held_locks:
            logger.trace("Attempting to extend lock {}", lock)
            new_lock = lock.model_copy(update={"expires_at_ns": perf_counter_ns() + time_helpers.second})
            await self._options.backend.acquire_extend_workflow_lock(new_lock, lock)
        # TODO: for each lock extended, pull the workflow and launch a loop


        # TODO: Check pending workflows (unclaimed)
        # TODO: Start expired locks loop (and run first one)

    async def stop(self):
        """
        Stops the runner gracefully for the fastest possible workflow resuming by another worker
        """
        # TODO: Shut down expired locks loop
        # TODO: Update each lock to have 1 time so it's priority recovered
        # TODO: Wait for current tasks to complete

    async def _workflow_loop(self, workflow: WorkflowInstance):
        """
        A loop for a single workflow
        """
        _workflow_execution_context.set({})
        # TODO: Fetch the history as needed
        # TODO: Execute the next step
        # TODO: Handle workflow completion
        # TODO: Handle workflow failure
        # TODO: Handle workflow create as new
