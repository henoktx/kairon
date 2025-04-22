from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from django.conf import settings

from executions.types.execution import UpdateExecutionParams
from executions.types.task_execution import UpdateTaskExecutionParams
from .types.workflow import WorkflowInput, WorkflowResult
from .types.task import TaskResult, TaskData, TaskType
from .types.status import Status

with workflow.unsafe.imports_passed_through():
    from .activities import (
        update_task_status_activity,
        update_execution_status_activity,
        send_email_activity,
    )


RETRY_DEFAULT_POLICY = RetryPolicy(
    backoff_coefficient=2,
    initial_interval=timedelta(seconds=10),
    maximum_attempts=5,
)

@workflow.defn
class KaironWorkflow:
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowResult:
        try:
            task_results = []
            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id, status=Status.RUNNING
                ),
                start_to_close_timeout=timedelta(seconds=10),
            )

            for task in input_data.tasks:
                result = await self._execute_task(task)
                task_results.append(result)

                if result.status == Status.FAILED:
                    raise Exception(f"Task {task.name} failed: {result.error_message}")

            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id, status=Status.COMPLETED
                ),
                start_to_close_timeout=timedelta(seconds=10),
                task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return WorkflowResult(
                execution_id=input_data.execution_id,
                status=Status.COMPLETED,
                task_results=task_results,
            )

        except RuntimeError as e:
            error_message = str(e)

            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id,
                    status=Status.FAILED,
                    error_message=error_message,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return WorkflowResult(
                execution_id=input_data.execution_id,
                status=Status.FAILED,
                task_results=task_results,
                error_message=error_message,
            )

    async def _execute_task(self, task: TaskData) -> TaskResult:
        await workflow.execute_activity(
            update_task_status_activity,
            UpdateTaskExecutionParams(
                task_execution_id=task.task_execution_id, status=Status.RUNNING
            ),
            start_to_close_timeout=timedelta(seconds=10),
            task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
            retry_policy=RETRY_DEFAULT_POLICY,
        )

        try:
            result = None
            if task.task_type == TaskType.EMAIL:
                result = await workflow.execute_activity(
                    send_email_activity,
                    task.email_config,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=task.retry_policy,
                )

            await workflow.execute_activity(
                update_task_status_activity,
                UpdateTaskExecutionParams(
                    task_execution_id=task.task_execution_id,
                    status=Status.COMPLETED,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return TaskResult(
                task_execution_id=task.task_execution_id,
                status=Status.COMPLETED,
                result=result,
            )

        except RuntimeError as e:
            error_message = str(e)

            await workflow.execute_activity(
                update_task_status_activity,
                UpdateTaskExecutionParams(
                    task_execution_id=task.task_execution_id,
                    status=Status.FAILED,
                    error_message=error_message,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return TaskResult(
                task_execution_id=task.task_execution_id,
                status=Status.FAILED,
                error_message=error_message,
            )
