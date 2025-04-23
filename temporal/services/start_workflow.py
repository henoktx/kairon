import uuid
from datetime import timedelta

from django.conf import settings
from temporalio.client import Client, WorkflowFailureError

from temporal.workflows import KaironWorkflow
from ..types.workflow import WorkflowInput


async def start_workflow(data: WorkflowInput) -> str:
    workflow_id = f"workflow-{uuid.uuid4()}"
    client = await Client.connect(settings.TEMPORAL_CLIENT_ADDRESS)

    try:

        await client.start_workflow(
            KaironWorkflow.run,
            data,
            id=workflow_id,
            task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
            task_timeout=timedelta(seconds=10),
            start_delay=timedelta(minutes=data.delay_minutes),
        )

        return workflow_id
    except WorkflowFailureError as e:
        raise RuntimeError(f"A execução falhou com erro: {e}")
