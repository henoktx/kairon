from datetime import timedelta
import uuid
from temporalio.client import Client, WorkflowFailureError

from ..types.workflow import WorkflowInput
from temporal.workflows import KaironWorkflow


async def start_workflow(data: WorkflowInput):
    workflow_id = f"workflow-{uuid.uuid4()}"
    client = await Client.connect("localhost:7233")

    try:
        workflow = await client.start_workflow(
            KaironWorkflow.run,
            data,
            id=workflow_id,
            task_queue="kairon-queue",
            task_timeout=timedelta(seconds=10),
        )

        return {"workflow_id": workflow.id, "workflow_run_id": workflow.run_id}
    except WorkflowFailureError as e:
        raise RuntimeError(f"Workflow execution failed: {e}")
