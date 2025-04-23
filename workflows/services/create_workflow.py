from ..models import Workflow, Task, Schedule, EmailTask, ReportTask
from executions.models import TaskExecution, Execution


def create_workflow(data, tasks_data, schedule_data=None) -> Workflow:
    workflow = Workflow.objects.create(**data)
    execution = Execution.objects.create(
        workflow=workflow, created_by=data["created_by"]
    )

    for task_data in tasks_data:
        email_config = task_data.pop("email_config", None)
        report_config = task_data.pop("report_config", None)

        task = Task.objects.create(
            workflow=workflow, created_by=data["created_by"], **task_data
        )
        task.execution = TaskExecution.objects.create(execution=execution, task=task)

        if email_config:
            EmailTask.objects.create(task=task, **email_config)
        elif report_config:
            ReportTask.objects.create(task=task, **report_config)

    if schedule_data:
        Schedule.objects.create(
            workflow=workflow,
            created_by=data["created_by"],
            **schedule_data,
        )

    return workflow
