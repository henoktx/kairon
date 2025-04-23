from asgiref.sync import sync_to_async
from temporalio import activity, exceptions

from executions.services.update_execution import update_execution_status
from executions.services.update_task_execution import (
    update_task_execution_status,
)
from executions.types.execution import UpdateExecutionParams
from executions.types.task_execution import UpdateTaskExecutionParams
from notifications.exceptions import EmailServiceError
from notifications.services.mailersend import MailerSendService
from notifications.types.email import EmailParams
from reports.services.report_generator import EmailReportGenerator
from reports.services.formart_report import format_report_as_html
from reports.types.report import ReportParams


@activity.defn
async def update_task_status_activity(
    task_execution_params: UpdateTaskExecutionParams,
) -> None:
    try:
        await sync_to_async(update_task_execution_status)(task_execution_params)
    except Exception as e:
        raise exceptions.ApplicationError(
            f"Erro ao atualizar o status da task: {str(e)}"
        )


@activity.defn
async def update_execution_status_activity(
    execution_params: UpdateExecutionParams,
) -> None:
    try:
        await sync_to_async(update_execution_status)(execution_params)
    except Exception as e:
        raise exceptions.ApplicationError(
            f"Erro ao atualizar o status do workflow: {str(e)}"
        )


@activity.defn
async def send_email_activity(email_params: EmailParams) -> None:
    email_service = MailerSendService()

    try:
        await sync_to_async(email_service.send_email)(email_params)
    except Exception as e:
        raise exceptions.ApplicationError(f"Erro no serviço de e-mail: {str(e)}")


@activity.defn
async def generate_report_activity(report_params: ReportParams) -> EmailParams:
    report_generator = EmailReportGenerator()
    try:
        report = await sync_to_async(report_generator.generate_report)(report_params)
        email_params = EmailParams(
                    subject=f"Envio de relatório de emails",
                    to_email=[report.user_email],
                    content="",
                    html_content=format_report_as_html(report)
                )
        return email_params
    except Exception as e:
        raise exceptions.ApplicationError(f"Erro na geração do relatório: {str(e)}")