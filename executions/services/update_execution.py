from django.db import transaction
from django.utils import timezone

from ..models import Execution
from ..types.execution import UpdateExecutionParams


def update_execution_status(execution_params: UpdateExecutionParams) -> None:
    with transaction.atomic():
        execution = Execution.objects.select_for_update().get(
            id=execution_params.execution_id
        )
        execution.status = execution_params.status

        if execution.status == "running":
            execution.started_at = timezone.now()
        if execution.status in ["completed", "failed", "canceled", "terminated"]:
            execution.completed_at = timezone.now()

        execution.error_message = execution_params.error_message or ""

        execution.save()
