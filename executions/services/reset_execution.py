from asgiref.sync import async_to_sync

from temporal.services.reset_workflow import reset_workflow
from ..models import Execution


def reset_execution(execution_id: int) -> None:
    try:
        execution = Execution.objects.get(id=execution_id)
        if execution.status != "failed":
            raise ValueError(
                "A execução só pode ser reiniciada se estiver com status 'failed'"
            )
        async_to_sync(reset_workflow)(execution.temporal_workflow_id)
    except Execution.DoesNotExist:
        raise ValueError(f"Execuação com id {execution_id} não existe.")
