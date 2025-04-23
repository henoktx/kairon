from asgiref.sync import sync_to_async
from temporalio import activity

from executions.services.update_execution import update_execution_status
from executions.services.update_task_execution import (
    update_task_execution_status,
)
from executions.types.execution import UpdateExecutionParams
from executions.types.task_execution import UpdateTaskExecutionParams
from notifications.exceptions import EmailServiceError
from notifications.services.mailersend import MailerSendService
from notifications.types.email import EmailParams


@activity.defn
async def update_task_status_activity(
    task_execution_params: UpdateTaskExecutionParams,
) -> None:
    try:
        await sync_to_async(update_task_execution_status)(task_execution_params)
    except Exception as e:
        raise RuntimeError(f"Erro ao atualizar o status da task: {str(e)}")


@activity.defn
async def update_execution_status_activity(
    execution_params: UpdateExecutionParams,
) -> None:
    try:
        await sync_to_async(update_execution_status)(execution_params)
    except Exception as e:
        raise RuntimeError(f"Erro ao atualizar o status do workflow: {str(e)}")


@activity.defn
async def send_email_activity(email_params: EmailParams) -> None:
    email_service = MailerSendService()

    try:
        success = await sync_to_async(email_service.send_email)(email_params)

        if not success:
            raise RuntimeError("Falha ao enviar e-mail")
    except EmailServiceError as e:
        raise RuntimeError(f"Erro no serviço de e-mail: {str(e)}")
