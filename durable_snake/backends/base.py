import contextvars
from typing import List

from ..internal.workflow_event import WorkflowEvent
from ..internal.workflow_lock import WorkflowLock
from ..workflow import WorkflowInstance

backend_context = contextvars.ContextVar[dict | None]("backend", default=None)


class BaseBackend:
    """
    The base backend class.
    Implement this to make a backend.
    """

    def __init__(self):
        pass

    async def close(self):
        """
        When the backend is closed, so you can gracefully shut down
        """
        pass

    async def create_workflow_instance(
            self,
            workflow: WorkflowInstance,
    ) -> str:
        """
        Creates a new workflow instance.

        TODO: add optimization for poking a worker instead of waiting for a list_pending_workflows

        :param workflow: A workflow that should be inserted if it does not exist (by ID).
        :returns: Workflow ID
        """
        raise NotImplementedError

    async def list_pending_workflows(self, queue: str) -> List[WorkflowInstance]:
        """
        Lists workflows that are pending to be picked up by a runner.
        You will likely want to return them in descending order by creation time, and have some limit.
        :return: List of workflows.
        """
        raise NotImplementedError

    async def get_workflow_instance(self, workflow_id: str) -> WorkflowInstance:
        """
        Gets a workflow instance by ID

        :param workflow_id: Workflow ID
        :return: Workflow instance
        """
        raise NotImplementedError

    async def update_workflow_instance(
            self,
            instance: WorkflowInstance,
            lock: WorkflowLock
    ):
        """
        Updates a workflow instance by ID

        :param instance: The workflow instance to update by ID
        :param lock: The currently held workflow lock you can use as a fencing token
        """
        raise NotImplementedError

    async def acquire_extend_workflow_lock(
            self,
            new_lock: WorkflowLock,
            old_lock: WorkflowLock = None,
    ) -> WorkflowLock:
        """
        Acquires or extends a workflow lock.
        If the old lock exists, the old_lock must exactly match what exists in the backend.

        :param new_lock: The new instance of the lock that will replace the old lock in the backend if able to
        successfully extend
        :param old_lock: Lock that is believed to be held by this runner, all information should match if
        exists, otherwise this is a new insert.
        :return: The updated workflow lock
        """
        raise NotImplementedError

    async def list_expired_locks(self) -> List[WorkflowLock]:
        """
        List workflow locks that have been expired that this runner can attempt to acquire.
        You should probably have some limit of how many locks you return, and maybe sort by how
        long the lock has been expired for (so you recover the oldest locks first).

        :return: List of expired locks
        """
        raise NotImplementedError

    async def insert_workflow_event_history(
            self,
            event: WorkflowEvent,
            lock: WorkflowLock
    ):
        """
        Insert a new workflow event to the history, unique by the (workflow_id, sequence_id)

        :param event: The workflow event
        :param lock: The expected currently held lock, allowing you to use the lock epoch as a fencing token
        inserting to the event history
        """
        raise NotImplementedError

    async def get_workflow_history(
            self,
            workflow_id: str,
            after_seq: int = None
    ) -> List[WorkflowEvent]:
        """
        Get a workflow's history in ascending sequence ID order
        :param workflow_id: Workflow ID to get the history for
        :param after_seq: If provided, only get the history after this sequence id
        :return: List of workflow events
        """
        raise NotImplementedError
