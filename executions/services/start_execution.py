from asgiref.sync import async_to_sync

from temporal.services.prepare_schedule import prepare_schedule_input
from temporal.services.prepare_workflow import prepare_workflow_input
from temporal.services.start_schedule import start_schedule
from temporal.services.start_workflow import start_workflow
from ..models import Execution


def start_execution(execution_id: int) -> None:
    try:
        execution = Execution.objects.get(pk=execution_id)
        workflow_input = prepare_workflow_input(execution)

        if hasattr(execution.workflow, "schedule"):
            schedule_input = prepare_schedule_input(execution)
            result = async_to_sync(start_schedule)(schedule_input, workflow_input)
        else:
            result = async_to_sync(start_workflow)(workflow_input)

        execution.temporal_workflow_id = result
        execution.save()

    except Execution.DoesNotExist:
        raise ValueError(f"Execuação com id {execution_id} não existe.")
