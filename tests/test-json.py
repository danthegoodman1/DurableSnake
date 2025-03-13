from durable_snake.workflow import WorkflowInstance, WorkflowStatus

instance = WorkflowInstance(id="id", status=WorkflowStatus.CREATED)
serialized = instance.model_dump_json()
print(serialized)
restored = WorkflowInstance.model_validate_json(serialized)
print(restored)