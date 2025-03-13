import contextvars

backend_context = contextvars.ContextVar[dict | None]("backend", default=None)


class BaseBackend:
    """
    The base backend class
    """

    def __init__(self):
        pass

    async def create_workflow_instance(
            self,
            id: str,
            *args,
            **kwargs,
    ):
        """
        Creates a workflow instance

        :arg id: Workflow ID. If this ID already exists, this call will raise an exception.
        """
        raise NotImplementedError
