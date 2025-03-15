import contextvars

# TODO: update the type
_workflow_execution_context = contextvars.ContextVar[dict | None]("workflow_execution", default=None)
