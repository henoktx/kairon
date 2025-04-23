from django.db import transaction
from django.utils import timezone

from ..models import TaskExecution
from ..types.task_execution import UpdateTaskExecutionParams


def update_task_execution_status(
    task_execution_params: UpdateTaskExecutionParams,
) -> None:
    with transaction.atomic():
        task_execution = TaskExecution.objects.get(
            id=task_execution_params.task_execution_id
        )
        task_execution.status = task_execution_params.status

        if task_execution.status == "running":
            task_execution.started_at = timezone.now()
        elif task_execution.status in ["completed", "failed"]:
            task_execution.completed_at = timezone.now()

        if task_execution_params.error_message:
            task_execution.error_message = task_execution_params.error_message

        task_execution.save()
