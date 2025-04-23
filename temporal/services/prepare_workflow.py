from executions.models import Execution, TaskExecution
from workflows.models import EmailTask
from ..types.workflow import WorkflowInput
from ..types.task import TaskData, TaskType
from notifications.types.email import EmailParams


def prepare_workflow_input(execution: Execution) -> WorkflowInput:
    tasks_data = []
    tasks_execution = TaskExecution.objects.filter(execution_id=execution.id)

    for task_execution in tasks_execution:
        task = task_execution.task

        task_data = TaskData(
            task_execution_id=task_execution.id,
            name=task.name,
            order=task.order,
            task_type=task.task_type,
            initial_interval=task.initial_interval,
            maximum_attempts=task.maximum_attempts,
            backoff_coefficient=task.back_off,
        )

        if task.task_type == TaskType.EMAIL.value:
            email_task = EmailTask.objects.get(task_id=task.id)
            email_config = EmailParams(
                to_email=email_task.get_recipients_list(),
                subject=email_task.subject,
                content=email_task.content,
                cc=email_task.get_cc_list(),
                from_email=email_task.task.created_by.email,
                from_name=email_task.task.created_by.first_name,
            )
            task_data.email_config = email_config

        tasks_data.append(task_data)

    return WorkflowInput(
        execution_id=execution.id,
        workflow_name=execution.workflow.name,
        tasks=sorted(tasks_data, key=lambda x: x.order),
        delay_minutes=execution.workflow.delay_minutes,
    )
