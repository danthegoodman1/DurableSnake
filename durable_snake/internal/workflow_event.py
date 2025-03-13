from enum import Enum

from pydantic import BaseModel, ConfigDict


class WorkflowEventType(Enum):
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_FINISHED = "workflow_finished"
    WORKFLOW_CONTINUED_AS_NEW = "workflow_continued_as_new"
    WORKFLOW_TERMINATED = "workflow_terminated"
    WORKFLOW_CANCELED = "workflow_canceled"

    CHILD_WORKFLOW_SCHEDULED = "child_workflow_scheduled"
    CHILD_WORKFLOW_CANCELLATION_REQUESTED = "child_workflow_cancellation_requested"
    CHILD_WORKFLOW_COMPLETED = "child_workflow_completed"
    CHILD_WORKFLOW_FAILED = "child_workflow_failed"

    ACTIVITY_STARTED = "activity_started"
    ACTIVITY_COMPLETED = "activity_completed"
    ACTIVITY_FAILED = "activity_failed"
    ACTIVITY_TIMED_OUT = "activity_timed_out"

    TIMER_SCHEDULED = "timer_scheduled"
    TIMER_FIRED = "timer_fired"
    TIMER_CANCELED = "timer_canceled"

    SIGNAL_RECEIVED = "signal_received"

    SIDE_EFFECT_RESULT = "side_effect_result"


class WorkflowEvent(BaseModel):
    """
    A workflow event
    """
    model_config = ConfigDict(frozen=True)  # events are immutable

    sequence_id: int
    """Monotonically increasing sequence number"""
    type: WorkflowEventType
