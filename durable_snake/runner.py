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

    _workflows = {}
    _workflow_locks = {}

    def __init__(self, options: RunnerOptions):
        self._options = options

    async def start(self):
        """
        Starts the runner
        """
        # TODO: Check pending workflows
        # TODO: Start expired locks loop (and run first one)

    async def stop(self):
        """
        Stops the runner gracefully for the fastest possible workflow resuming by another worker
        """
        # TODO: Shut down expired locks loop
        # TODO: Update each lock to have 1 time so it's priority recovered
        # TODO: Wait for current tasks to complete
