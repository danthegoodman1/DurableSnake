import contextvars
from typing import List

from ..workflow import WorkflowInstance

backend_context = contextvars.ContextVar[dict | None]("backend", default=None)


class BaseBackend:
    """
    The base backend class
    """

    def __init__(self):
        pass

    async def create_workflow_instance(
            self,
            *args,
            id: str | None = None,
            data: dict | List | None = None,
            **kwargs,
    ) -> str:
        """
        Creates a workflow instance

        :arg id: Workflow ID. If provided, then it will serve as a unique ID that will be deduplicated against.
        If not provided, then the workflow will generate its own ID
        :arg data: Data to pass into the workflow instance

        :returns: Workflow ID
        """
        raise NotImplementedError

    async def get_workflow_instance(
            self
    ) -> WorkflowInstance:
        """
        Gets a workflow instance from storage

        :return: Workflow instance
        """
        raise NotImplementedError