from enum import Enum
from pydantic import BaseModel


class WorkflowStatus(Enum):
    # Open workflows
    PENDING = "pending"
    RUNNING = "running"

    # Closed workflows
    TERMINATED = "terminated"
    CONTINUED_AS_NEW = "continued_as_new"
    CANCELLED = "cancelled"
    FAILED = "failed"
    TIMED_OUT = "timed_out"



class WorkflowInstance(BaseModel):
    """
    High level info about a workflow instance
    """

    id: str
    """The ID of the instance"""
    type: str
    """The type of workflow"""
    status: WorkflowStatus
    queue: str
    created_ns: int
    started_ns: int
    closed_ns: int
    parent_id: str | None = None
    data: dict | None = None

    # Updatable fields
    history_length: int = 0
    history_bytes: int = 0

