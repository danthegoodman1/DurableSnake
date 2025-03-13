from pydantic import BaseModel


class WorkflowLock(BaseModel):
    """
    A workflow lock that is either held or expired.
    """
    workflow_id: str
    epoch: int = 0
    """
    An monotonically incrementing integer that serves as a fencing token for lock extensions and
    history insertions
    """
    expires_at_ns: int
    """When the lock expires in epoch nanoseconds"""
    runner_id: str
    """The ID of the runner that most recently acquired the lock"""