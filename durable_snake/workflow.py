from enum import Enum

from pydantic import BaseModel


class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"


class WorkflowInstance(BaseModel):
    id: str
    status: WorkflowStatus
