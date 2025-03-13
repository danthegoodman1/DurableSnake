import contextvars
from typing import List

from ..internal.workflow_event import WorkflowEvent
from ..internal.workflow_lock import WorkflowLock
from ..workflow import WorkflowInstance

backend_context = contextvars.ContextVar[dict | None]("backend", default=None)


class BaseBackend:
    """
    The base backend class. Implement this to make a backend.
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
            *args,
            workflow_id: str | None = None,
            data: dict | List | None = None,
            **kwargs,
    ) -> str:
        """
        Creates a workflow instance

        :param workflow_id: Unique workflow ID. If provided, then it will serve as a unique ID that will be
        deduplicated against. If not provided, then the workflow ID will be generated.
        :param data: Data to pass into the workflow instance

        :returns: Workflow ID
        """
        raise NotImplementedError

    async def get_workflow_instance(self, workflow_id: str) -> WorkflowInstance:
        """
        Gets a workflow instance by ID.

        :param workflow_id: Workflow ID
        :return: Workflow instance
        """
        raise NotImplementedError

    async def update_workflow_instance(self, instance: WorkflowInstance):
        """
        Updates a workflow instance
        """
        raise NotImplementedError

    async def acquire_workflow_lock(
            self,
            workflow_id: str,
            runner_id: str,
            expire_at_ns: int
    ) -> WorkflowLock | None:
        """
        Acquires a lock on a workflow if the lock doesn't exist, or is expired.
        Must do so with serializable consistency.

        If the lock exists and is expired, then the epoch must be incremented and the runner_id updated.

        Must return None if the lock was unable to be acquired due to a concurrent lock acquisition.

        :param workflow_id: Workflow ID
        :param runner_id: Runner ID
        :param expire_at_ns: Lock expiry time in nanoseconds
        :returns: A workflow lock
        """
        raise NotImplementedError

    async def extend_workflow_lock(
            self,
            lock: WorkflowLock,
            expire_at_ns: int
    ) -> WorkflowLock:
        """
        Extends a lock that has not yet expired with serializable consistency.

        It must only be permitted to do so if:
            1. The runner_id is the same as the currently stored lock
            2. The epoch is the same
            3. The lock is not expired

        When the lock is extended, the epoch must be incremented by one, and the

        :param lock: Lock that is currently held by this runner
        :param expire_at_ns: The new lock expiry time in nanoseconds
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

    async def append_workflow_event_history(self, event: WorkflowEvent):
        """
        Appends a workflow event to the history
        :param event: The workflow event
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
