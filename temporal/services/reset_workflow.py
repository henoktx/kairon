from django.conf import settings
from temporalio.api.workflowservice.v1 import ResetWorkflowExecutionRequest
from temporalio.api.common.v1 import WorkflowExecution
from temporalio.api.enums.v1 import EventType

from ..client import get_temporal_client


async def reset_workflow(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id=workflow_id)

    async for event in handle.fetch_history_events():
        if event.event_type == EventType.EVENT_TYPE_ACTIVITY_TASK_FAILED:
            break
        if event.event_type == EventType.EVENT_TYPE_WORKFLOW_TASK_COMPLETED:
            event_id = event.event_id

    await client.workflow_service.reset_workflow_execution(
        ResetWorkflowExecutionRequest(
            namespace=settings.TEMPORAL_CLIENT_NAMESPACE,
            request_id="reset-failed-workflow",
            workflow_execution=WorkflowExecution(workflow_id=workflow_id),
            workflow_task_finish_event_id=event_id)
        )