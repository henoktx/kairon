from django.test import TestCase
from model_bakery import baker

from executions.models import Execution, TaskExecution
from workflows.models import Workflow, Task, Schedule, EmailTask, ReportTask
from workflows.services.create_workflow import create_workflow


class CreateWorkflowServiceTest(TestCase):
    def setUp(self):
        self.user = baker.make("users.User")

        self.workflow_data = {
            "name": "Test Workflow",
            "description": "Test workflow description",
            "created_by": self.user,
            "delay_minutes": 5,
        }

        self.email_task_data = [
            {
                "name": "Send Email Task",
                "description": "Task to send email",
                "order": 1,
                "task_type": "email",
                "maximum_attempts": 3,
                "initial_interval": 10,
                "back_off": 1.5,
                "email_config": {
                    "recipients": "test@example.com, another@example.com",
                    "subject": "Test Email Subject",
                    "content": "This is a test email content",
                    "cc": "cc@example.com",
                },
            }
        ]

        self.report_task_data = [
            {
                "name": "Generate Report Task",
                "description": "Task to generate report",
                "order": 1,
                "task_type": "report",
                "maximum_attempts": 3,
                "initial_interval": 10,
                "back_off": 1.5,
                "report_config": {"filter_type": "last_day"},
            }
        ]

        self.mixed_tasks_data = self.email_task_data + [
            {
                "name": "Generate Report Task",
                "description": "Task to generate report",
                "order": 2,
                "task_type": "report",
                "maximum_attempts": 3,
                "initial_interval": 10,
                "back_off": 1.5,
                "report_config": {"filter_type": "last_week"},
            }
        ]

        self.schedule_data = {
            "minute": 0,
            "hour": 8,
            "day_of_month": None,
            "day_of_week": None,
        }

    def test_create_workflow_with_email_task(self):
        workflow = create_workflow(self.workflow_data, self.email_task_data)

        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Execution.objects.count(), 1)
        self.assertEqual(TaskExecution.objects.count(), 1)
        self.assertEqual(EmailTask.objects.count(), 1)
        self.assertEqual(ReportTask.objects.count(), 0)
        self.assertEqual(Schedule.objects.count(), 0)

        created_task = Task.objects.first()
        self.assertEqual(created_task.name, "Send Email Task")
        self.assertEqual(created_task.task_type, "email")

        email_config = EmailTask.objects.first()
        self.assertEqual(email_config.task, created_task)
        self.assertEqual(email_config.subject, "Test Email Subject")
        self.assertEqual(len(email_config.get_recipients_list()), 2)

        execution = Execution.objects.first()
        self.assertEqual(execution.workflow, workflow)
        self.assertEqual(execution.created_by, self.user)
        self.assertEqual(execution.status, "running")

    def test_create_workflow_with_report_task(self):
        workflow = create_workflow(self.workflow_data, self.report_task_data)

        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Execution.objects.count(), 1)
        self.assertEqual(TaskExecution.objects.count(), 1)
        self.assertEqual(EmailTask.objects.count(), 0)
        self.assertEqual(ReportTask.objects.count(), 1)
        self.assertEqual(Schedule.objects.count(), 0)

        created_task = Task.objects.first()
        self.assertEqual(created_task.name, "Generate Report Task")
        self.assertEqual(created_task.task_type, "report")

        report_config = ReportTask.objects.first()
        self.assertEqual(report_config.task, created_task)
        self.assertEqual(report_config.filter_type, "last_day")

    def test_create_workflow_with_schedule(self):
        workflow = create_workflow(
            self.workflow_data, self.email_task_data, self.schedule_data
        )

        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Execution.objects.count(), 1)
        self.assertEqual(TaskExecution.objects.count(), 1)
        self.assertEqual(Schedule.objects.count(), 1)

        schedule = Schedule.objects.first()
        self.assertEqual(schedule.workflow, workflow)
        self.assertEqual(schedule.minute, 0)
        self.assertEqual(schedule.hour, 8)
        self.assertIsNone(schedule.day_of_month)
        self.assertIsNone(schedule.day_of_week)

    def test_create_workflow_with_mixed_tasks(self):
        workflow = create_workflow(self.workflow_data, self.mixed_tasks_data)

        self.assertEqual(Workflow.objects.count(), 1)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Execution.objects.count(), 1)
        self.assertEqual(TaskExecution.objects.count(), 2)
        self.assertEqual(EmailTask.objects.count(), 1)
        self.assertEqual(ReportTask.objects.count(), 1)

        email_task = Task.objects.get(task_type="email")
        report_task = Task.objects.get(task_type="report")

        self.assertEqual(email_task.order, 1)
        self.assertEqual(report_task.order, 2)

        execution = Execution.objects.first()
        task_executions = TaskExecution.objects.filter(execution=execution)
        self.assertEqual(task_executions.count(), 2)
