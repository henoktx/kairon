from datetime import timedelta

from temporalio import workflow, exceptions
from temporalio.common import RetryPolicy

from .types.task import TaskResult, TaskData
from .types.workflow import WorkflowInput

with workflow.unsafe.imports_passed_through():
    from executions.types.execution import UpdateExecutionParams
    from executions.types.task_execution import UpdateTaskExecutionParams
    from .activities import (
        update_task_status_activity,
        update_execution_status_activity,
        send_email_activity,
        generate_report_activity,
    )


RETRY_DEFAULT_POLICY = RetryPolicy(
    backoff_coefficient=2,
    initial_interval=timedelta(seconds=10),
    maximum_attempts=5,
)


@workflow.defn
class KaironWorkflow:
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> None:
        try:
            task_results = []
            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id, status="running"
                ),
                start_to_close_timeout=timedelta(seconds=10),
            )

            for task in input_data.tasks:
                result = await self._execute_task(task)
                task_results.append(result)

                if result.status == "failed":
                    raise exceptions.ApplicationError(
                        f"Task {task.name} failed: {result.error_message}"
                    )

            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id, status="completed"
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RETRY_DEFAULT_POLICY,
            )
        except exceptions.TemporalError as e:
            error_message = str(e)

            await workflow.execute_activity(
                update_execution_status_activity,
                UpdateExecutionParams(
                    execution_id=input_data.execution_id,
                    status="failed",
                    error_message=error_message,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RETRY_DEFAULT_POLICY,
            )

    async def _execute_task(self, task: TaskData) -> TaskResult:
        await workflow.execute_activity(
            update_task_status_activity,
            UpdateTaskExecutionParams(
                task_execution_id=task.task_execution_id, status="running"
            ),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RETRY_DEFAULT_POLICY,
        )

        TASK_RETRY_POLICY = RetryPolicy(
            initial_interval=timedelta(seconds=task.initial_interval),
            maximum_attempts=task.maximum_attempts,
            backoff_coefficient=task.backoff_coefficient,
        )

        try:
            if task.task_type == "email":
                await workflow.execute_activity(
                    send_email_activity,
                    task.email_config,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=TASK_RETRY_POLICY,
                )

            elif task.task_type == "report":
                report = await workflow.execute_activity(
                    generate_report_activity,
                    task.report_config,
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=TASK_RETRY_POLICY,
                )

                await workflow.execute_activity(
                    send_email_activity,
                    report,
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=TASK_RETRY_POLICY,
                )

            await workflow.execute_activity(
                update_task_status_activity,
                UpdateTaskExecutionParams(
                    task_execution_id=task.task_execution_id,
                    status="completed",
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return TaskResult(
                task_execution_id=task.task_execution_id, status="completed"
            )

        except exceptions.TemporalError as e:
            error_message = str(e)

            await workflow.execute_activity(
                update_task_status_activity,
                UpdateTaskExecutionParams(
                    task_execution_id=task.task_execution_id,
                    status="failed",
                    error_message=error_message,
                ),
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RETRY_DEFAULT_POLICY,
            )

            return TaskResult(
                task_execution_id=task.task_execution_id,
                status="failed",
                error_message=error_message,
            )
