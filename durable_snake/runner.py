import asyncio
from dataclasses import dataclass
from loguru import logger
from time import perf_counter_ns

from durable_snake.internal.workflow_lock import WorkflowLock

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

    shutdown_activity_timeout_sec: float = 5.0
    """How long to wait for the runner to stop all activities before shutting down"""


@dataclass
class _RunnerWorkflow:
    workflow: WorkflowInstance
    lock: WorkflowLock
    task: asyncio.Task


class Runner:
    """
    The workflow runner.
    """

    _workflows: dict[str, _RunnerWorkflow] = {}
    _expired_locks_task: asyncio.Task | None = None

    def __init__(self, options: RunnerOptions):
        self._options = options
        logger.debug("Runner {} initialized", self._options.id)

    async def start(self):
        """
        Starts the runner
        """
        # Check for open locks that are owned by this runner
        held_locks = await self._options.backend.list_locks_held_by_runner(
            self._options.id
        )
        logger.trace("Found {} held locks", len(held_locks))

        # Try to extend the locks
        for lock in held_locks:
            logger.trace("Attempting to extend lock {}", lock)
            new_lock = lock.model_copy(
                update={"expires_at_ns": perf_counter_ns() + time_helpers.second}
            )
            updated_lock = await self._options.backend.acquire_extend_workflow_lock(
                new_lock, lock
            )
            if updated_lock is not None:
                logger.trace("Extended lock for workflow {}", updated_lock.workflow_id)
                # Get the workflow and launch a loop
                workflow = await self._options.backend.get_workflow_instance(
                    updated_lock.workflow_id
                )
                task = asyncio.create_task(self._workflow_loop(workflow))
                self._workflows[updated_lock.workflow_id] = _RunnerWorkflow(
                    workflow=workflow, lock=updated_lock, task=task
                )

        # Check pending workflows (unclaimed)
        pending_workflows = await self._options.backend.list_pending_workflows(
            self._options.queue
        )
        logger.trace("Found {} pending workflows", len(pending_workflows))
        for workflow in pending_workflows:
            # Attempt to acquire the lock
            lock = await self._options.backend.acquire_extend_workflow_lock(
                WorkflowLock(
                    workflow_id=workflow.id,
                    epoch=0,
                    expires_at_ns=int(
                        perf_counter_ns()
                        + time_helpers.second
                        * self._options.workflow_lock_expiration_sec
                    ),
                    runner_id=self._options.id,
                )
            )

            if lock is None:
                logger.trace(
                    "Failed to acquire lock for workflow {}, continuing", workflow.id
                )
                continue

            task = asyncio.create_task(self._workflow_loop(workflow))
            self._workflows[workflow.id] = _RunnerWorkflow(
                workflow=workflow, lock=lock, task=task
            )

        # Start expired locks loop (and run first one)
        self._expired_locks_task = asyncio.create_task(self._expired_locks_loop())

    async def stop(self):
        """
        Stops the runner gracefully for the fastest possible workflow resuming by another worker
        """
        logger.debug("Stopping runner {}", self._options.id)

        # Cancel expired locks loop
        if self._expired_locks_task is not None:
            self._expired_locks_task.cancel()

        # Cancel all workflow tasks
        pending_tasks = []
        for workflow_id, workflow_data in list(self._workflows.items()):
            if workflow_data.task and not workflow_data.task.done():
                logger.trace("Cancelling workflow task for {}", workflow_id)
                workflow_data.task.cancel()
                pending_tasks.append(workflow_data.task)

        # Wait for all tasks to complete (with timeout protection)
        if pending_tasks:
            logger.debug(
                "Waiting for {} workflow tasks to complete", len(pending_tasks)
            )
            try:
                await asyncio.wait(
                    pending_tasks,
                    timeout=self._options.shutdown_activity_timeout_sec,
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for workflow tasks to complete")

        # Update each lock to have 1 time so it's priority recovered
        for workflow_id, workflow_data in self._workflows.items():
            workflow_data.lock.model_copy(
                update={"epoch": workflow_data.lock.epoch + 1}
            )
            logger.trace("Incrementing epoch for lock {}", workflow_data.lock)
            await self._options.backend.update_workflow_instance(
                workflow_data.workflow, workflow_data.lock
            )

        logger.debug("Runner {} stopped", self._options.id)

    async def _workflow_loop(self, workflow: WorkflowInstance):
        """
        A loop for a single workflow
        """
        logger.trace("Starting workflow loop for {}", workflow.id)
        _workflow_execution_context.set({})
        # TODO: Fetch the history as needed
        # TODO: Execute the next step
        # TODO: Handle workflow completion
        # TODO: Handle workflow failure
        # TODO: Handle workflow create as new

    async def _expired_locks_loop(self):
        """
        A loop for checking for expired locks
        """
        while True:
            await asyncio.sleep(self._options.expired_locks_poll_sec)
            expired_locks = await self._options.backend.list_expired_locks()
            for lock in expired_locks:
                logger.trace("Lock {} has expired", lock)
                # TODO: Attempt to acquire the lock
                # TODO: If successful, add to workflows
