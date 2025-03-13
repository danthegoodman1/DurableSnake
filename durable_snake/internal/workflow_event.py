from enum import Enum

from pydantic import BaseModel

class WorkflowEventStatus(Enum):
    SCHEDULED = "scheduled"
    STARTED = "started"
    COMPLETED = "completed"
    FAILING = "failing"
    FAILED = "failed"

class WorkflowEvent(BaseModel):
    """
    A workflow event
    """
    id: int
    """Sequentially incrementing integer"""
    status: WorkflowEventStatus