from dataclasses import dataclass, field

@dataclass
class RunnerOptions:
    queue: str
    expired_locks_poll_sec: float = 5.0
    step_concurrency: int = 0
    """Max number of steps that can be running at once. 0 means no limit"""
    pending_workflows_poll_sec: float = 2.0

class Runner:
    """
    The workflow runner.
    """

    def __init__(self, options: RunnerOptions):
        self._options = options