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
            workflow: WorkflowInstance
    ) -> str:
        """
        Creates a new workflow instance

        :param workflow: A workflow that should be inserted if it does not exist (by ID).
        :returns: Workflow ID
        """
        raise NotImplementedError

    async def get_workflow_instance(self, workflow_id: str) -> WorkflowInstance:
        """
        Gets a workflow instance by ID

        :param workflow_id: Workflow ID
        :return: Workflow instance
        """
        raise NotImplementedError

    async def update_workflow_instance(self, instance: WorkflowInstance):
        """
        Updates a workflow instance by ID
        """
        raise NotImplementedError

    async def take_workflow_lock(
            self,
            new_lock: WorkflowLock,
            old_lock: WorkflowLock = None,
    ) -> WorkflowLock:
        """
        Acquires or extends a lock with serializable consistency.
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

    async def append_workflow_event_history(
            self,
            event: WorkflowEvent,
            lock: WorkflowLock
    ):
        """
        Appends a workflow event to the history
        :param event: The workflow event
        :param lock: The currently held lock, allowing you to use the lock epoch as a fencing token for
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
