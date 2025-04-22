from asgiref.sync import async_to_sync

from ..models import Execution
from temporal.services.prepare_workflow import prepare_workflow_input
from temporal.services.start_workflow import start_workflow


def start_execution(execution_id: int) -> bool:
    execution = Execution.objects.get(pk=execution_id)
    workflow_input = prepare_workflow_input(execution)

    result = async_to_sync(start_workflow)(workflow_input)
    execution.temporal_workflow_id = result["workflow_id"]
    execution.temporal_workflow_run_id = result["workflow_run_id"]
    execution.save()

    return True