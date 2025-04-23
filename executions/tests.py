from unittest.mock import patch

from django.test import TestCase

from executions.models import Execution
from executions.services.reset_execution import reset_execution
from executions.services.start_execution import start_execution
from users.models import User
from workflows.models import Workflow, Task, Schedule


class ExecutionServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        self.workflow_without_schedule = Workflow.objects.create(
            name="Test Workflow",
            description="Workflow for testing",
            created_by=self.user,
        )

        self.task = Task.objects.create(
            workflow=self.workflow_without_schedule,
            created_by=self.user,
            name="Test Task",
            description="Task for testing",
            order=1,
            task_type="report",
            maximum_attempts=3,
            initial_interval=10,
            back_off=1.5,
        )

        self.workflow_with_schedule = Workflow.objects.create(
            name="Test Workflow with Schedule",
            description="Workflow with schedule for testing",
            created_by=self.user,
        )

        Task.objects.create(
            workflow=self.workflow_with_schedule,
            created_by=self.user,
            name="Scheduled Task",
            description="Scheduled task for testing",
            order=1,
            task_type="report",
            maximum_attempts=3,
            initial_interval=10,
            back_off=1.5,
        )

        self.schedule = Schedule.objects.create(
            workflow=self.workflow_with_schedule,
            created_by=self.user,
            minute=0,
            hour=0,
            day_of_month=None,
            day_of_week=None,
        )

        self.execution_without_schedule = Execution.objects.create(
            workflow=self.workflow_without_schedule,
            created_by=self.user,
            status="running",
        )

        self.execution_with_schedule = Execution.objects.create(
            workflow=self.workflow_with_schedule, created_by=self.user, status="running"
        )

        self.failed_execution = Execution.objects.create(
            workflow=self.workflow_without_schedule,
            created_by=self.user,
            status="failed",
            temporal_workflow_id="test_temporal_id_123",
            error_message="Test error message",
        )

    def test_start_execution_without_schedule(self):
        with patch(
            "executions.services.start_execution.async_to_sync"
        ) as mock_async_to_sync:
            mock_async_to_sync.return_value = (
                lambda *args, **kwargs: "mock_workflow_id_123"
            )

            start_execution(self.execution_without_schedule.id)

            self.assertTrue(mock_async_to_sync.called)

            self.execution_without_schedule.refresh_from_db()

            self.assertEqual(
                self.execution_without_schedule.temporal_workflow_id,
                "mock_workflow_id_123",
            )
            self.assertEqual(self.execution_without_schedule.status, "running")

    def test_start_execution_with_schedule(self):
        with patch(
            "executions.services.start_execution.async_to_sync"
        ) as mock_async_to_sync:
            mock_async_to_sync.return_value = (
                lambda *args, **kwargs: "mock_schedule_workflow_id_456"
            )

            start_execution(self.execution_with_schedule.id)

            self.assertTrue(mock_async_to_sync.called)

            self.execution_with_schedule.refresh_from_db()

            self.assertEqual(
                self.execution_with_schedule.temporal_workflow_id,
                "mock_schedule_workflow_id_456",
            )
            self.assertEqual(self.execution_with_schedule.status, "running")

    def test_start_execution_not_found(self):
        non_existent_id = 99999

        with self.assertRaises(ValueError) as context:
            start_execution(non_existent_id)

        self.assertIn("não existe", str(context.exception))

    def test_reset_execution_success(self):
        def set_execution_to_running(*args, **kwargs):
            execution = Execution.objects.get(id=self.failed_execution.id)
            execution.status = "running"
            execution.save()
            return None

        with patch(
            "executions.services.reset_execution.async_to_sync"
        ) as mock_async_to_sync:
            mock_async_to_sync.return_value = (
                lambda *args, **kwargs: set_execution_to_running()
            )

            reset_execution(self.failed_execution.id)

            self.assertTrue(mock_async_to_sync.called)

            self.failed_execution.refresh_from_db()

            self.assertEqual(self.failed_execution.status, "running")

    def test_reset_execution_not_failed(self):
        with self.assertRaises(ValueError) as context:
            reset_execution(self.execution_without_schedule.id)

        self.assertIn("status 'failed'", str(context.exception))

    def test_reset_execution_not_found(self):
        non_existent_id = 99999

        with self.assertRaises(ValueError) as context:
            reset_execution(non_existent_id)

        self.assertIn("não existe", str(context.exception))
