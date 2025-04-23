import uuid

from django.conf import settings
from temporalio.client import (
    ScheduleCalendarSpec,
    ScheduleSpec,
    ScheduleAlreadyRunningError,
    Schedule,
    ScheduleActionStartWorkflow,
)

from ..client import get_temporal_client
from ..types.workflow import WorkflowInput
from ..workflows import KaironWorkflow


async def start_schedule(
    calendar_spec: ScheduleCalendarSpec, workflow_data: WorkflowInput
):
    schedule_id = f"schedule-{uuid.uuid4()}"
    workflow_id = f"workflow-{uuid.uuid4()}"
    client = await get_temporal_client()

    try:
        await client.create_schedule(
            schedule_id,
            Schedule(
                action=ScheduleActionStartWorkflow(
                    KaironWorkflow.run,
                    workflow_data,
                    id=workflow_id,
                    task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
                ),
                spec=ScheduleSpec(calendars=[calendar_spec]),
            ),
        )

        return {"workflow_id": workflow_id}
    except ScheduleAlreadyRunningError as e:
        raise RuntimeError(f"A execução falhou com erro: {e}")
