from django.utils import timezone
from django.db import transaction

from ..models import Execution
from ..types.execution import UpdateExecutionParams


def update_execution_status(execution_params: UpdateExecutionParams) -> None:
    with transaction.atomic():
        execution = Execution.objects.select_for_update().get(
            id=execution_params.execution_id
        )
        execution.status = execution_params.status

        if execution.status in ["completed", "failed", "canceled", "terminated"]:
            execution.completed_at = timezone.now()

        if execution_params.error_message:
            execution.error_message = execution_params.error_message

        execution.save()

        # return {
        #     "id": execution.id,
        #     "status": execution.status,
        #     "started_at": execution.started_at,
        #     "completed_at": execution.completed_at,
        # }
