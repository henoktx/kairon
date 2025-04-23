from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from executions.models import TaskExecution, Execution
from reports.services.report_generator import EmailReportGenerator
from reports.types.report import ReportParams
from users.models import User
from workflows.models import Task, Workflow, EmailTask


class EmailReportGeneratorTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")
        self.user3 = User.objects.create(username="user3", email="user3@example.com")

        self.workflow1 = Workflow.objects.create(
            name="Workflow 1", created_by=self.user1
        )
        self.workflow2 = Workflow.objects.create(
            name="Workflow 2", created_by=self.user2
        )
        self.workflow3 = Workflow.objects.create(
            name="Workflow 3", created_by=self.user3
        )

        self.task1 = Task.objects.create(
            workflow=self.workflow1,
            created_by=self.user1,
            name="Email Task 1",
            task_type="email",
            order=1,
        )
        self.task2 = Task.objects.create(
            workflow=self.workflow2,
            created_by=self.user2,
            name="Email Task 2",
            task_type="email",
            order=1,
        )
        self.task3 = Task.objects.create(
            workflow=self.workflow3,
            created_by=self.user3,
            name="Email Task 3",
            task_type="email",
            order=1,
        )

        self.email_config1 = EmailTask.objects.create(
            task=self.task1,
            recipients="john@example.com,jane@example.com",
            subject="Test Email 1",
            content="Test content",
            cc="manager@example.com",
        )
        self.email_config2 = EmailTask.objects.create(
            task=self.task2,
            recipients="peter@example.com",
            subject="Test Email 2",
            content="Test content",
        )
        self.email_config3 = EmailTask.objects.create(
            task=self.task3,
            recipients="john@example.com,sarah@example.com,mike@example.com",
            subject="Test Email 3",
            content="Test content",
            cc="director@example.com,manager@example.com",
        )

        self.execution1 = Execution.objects.create(
            workflow=self.workflow1, created_by=self.user1
        )
        self.execution2 = Execution.objects.create(
            workflow=self.workflow2, created_by=self.user2
        )
        self.execution3 = Execution.objects.create(
            workflow=self.workflow3, created_by=self.user3
        )

        self.now = timezone.now()
        self.hour_ago = self.now - timedelta(hours=1)
        self.day_ago = self.now - timedelta(days=1)
        self.week_ago = self.now - timedelta(days=7)
        self.month_ago = self.now - timedelta(days=30)

        self._create_task_executions()

    def _create_task_executions(self):
        for _ in range(3):
            TaskExecution.objects.create(
                task=self.task1,
                execution=self.execution1,
                status="completed",
                started_at=self.now - timedelta(minutes=30),
                completed_at=self.now - timedelta(minutes=29),
            )

        for _ in range(2):
            TaskExecution.objects.create(
                task=self.task1,
                execution=self.execution1,
                status="failed",
                started_at=self.now - timedelta(minutes=20),
                completed_at=self.now - timedelta(minutes=19),
                error_message="Delivery failed",
            )

        TaskExecution.objects.create(
            task=self.task2,
            execution=self.execution2,
            status="completed",
            started_at=self.now - timedelta(minutes=10),
            completed_at=self.now - timedelta(minutes=9),
        )

        for _ in range(2):
            TaskExecution.objects.create(
                task=self.task1,
                execution=self.execution1,
                status="completed",
                started_at=self.now - timedelta(hours=5),
                completed_at=self.now - timedelta(hours=4, minutes=50),
            )

        for _ in range(3):
            TaskExecution.objects.create(
                task=self.task1,
                execution=self.execution1,
                status="completed",
                started_at=self.now - timedelta(days=3),
                completed_at=self.now - timedelta(days=3, minutes=-10),
            )

        for _ in range(2):
            TaskExecution.objects.create(
                task=self.task1,
                execution=self.execution1,
                status="failed",
                started_at=self.now - timedelta(days=15),
                completed_at=self.now - timedelta(days=15, minutes=-5),
                error_message="Server unreachable",
            )

        TaskExecution.objects.create(
            task=self.task3,
            execution=self.execution3,
            status="completed",
            started_at=self.now - timedelta(minutes=15),
            completed_at=self.now - timedelta(minutes=14),
        )

        TaskExecution.objects.create(
            task=self.task3,
            execution=self.execution3,
            status="completed",
            started_at=self.now - timedelta(days=2),
            completed_at=self.now - timedelta(days=2, minutes=-5),
        )

    def test_email_report_basic_generation(self):
        generator = EmailReportGenerator()
        params = ReportParams(user_id=self.user1.id, filter_type="last_hour")

        report = generator.generate_report(params)

        self.assertEqual(report.user_email, self.user1.email)
        self.assertTrue(report.period_start < report.period_end)

        stats = report.stats
        self.assertEqual(stats.total_sent, 5)
        self.assertEqual(stats.successful_deliveries, 3)
        self.assertEqual(stats.failed_deliveries, 2)
        self.assertEqual(stats.total_recipients, 15)
        self.assertEqual(stats.unique_recipients, 3)
        self.assertEqual(stats.average_delivery_time, 60.0)

        self.assertEqual(len(report.most_common_recipients), 3)
        recipient_counts = {
            r["email"]: r["count"] for r in report.most_common_recipients
        }
        self.assertEqual(recipient_counts["john@example.com"], 5)
        self.assertEqual(recipient_counts["jane@example.com"], 5)
        self.assertEqual(recipient_counts["manager@example.com"], 5)

    def test_report_for_different_periods(self):
        generator = EmailReportGenerator()

        filter_types = ["last_hour", "last_day", "last_week", "last_month"]
        expected_totals = {
            "last_hour": 5,
            "last_day": 7,
            "last_week": 10,
            "last_month": 12,
        }

        for filter_type in filter_types:
            with self.subTest(filter_type=filter_type):
                params = ReportParams(user_id=self.user1.id, filter_type=filter_type)
                report = generator.generate_report(params)
                self.assertEqual(
                    report.stats.total_sent,
                    expected_totals[filter_type],
                    f"Expected {expected_totals[filter_type]} for {filter_type}",
                )

                self.assertEqual(
                    report.stats.total_recipients,
                    expected_totals[filter_type] * 3,
                    f"Expected {expected_totals[filter_type] * 3} recipients for {filter_type}",
                )

    def test_report_with_no_data(self):
        new_user = User.objects.create(username="newuser", email="new@example.com")

        generator = EmailReportGenerator()
        params = ReportParams(user_id=new_user.id, filter_type="last_hour")

        report = generator.generate_report(params)

        self.assertEqual(report.stats.total_sent, 0)
        self.assertEqual(report.stats.successful_deliveries, 0)
        self.assertEqual(report.stats.failed_deliveries, 0)
        self.assertEqual(report.stats.total_recipients, 0)
        self.assertEqual(report.stats.unique_recipients, 0)
        self.assertEqual(len(report.most_common_recipients), 0)

    def test_report_with_multiple_recipients(self):
        generator = EmailReportGenerator()
        params = ReportParams(user_id=self.user3.id, filter_type="last_day")

        report = generator.generate_report(params)

        self.assertEqual(report.stats.total_sent, 1)
        self.assertEqual(report.stats.total_recipients, 5)
        self.assertEqual(report.stats.unique_recipients, 5)

        recipient_counts = {
            r["email"]: r["count"] for r in report.most_common_recipients
        }
        self.assertEqual(len(recipient_counts), 5)
        for email in [
            "john@example.com",
            "sarah@example.com",
            "mike@example.com",
            "director@example.com",
            "manager@example.com",
        ]:
            self.assertEqual(recipient_counts[email], 1)

    def test_invalid_user(self):
        generator = EmailReportGenerator()
        params = ReportParams(user_id=9999, filter_type="last_hour")

        with self.assertRaises(ValueError):
            generator.generate_report(params)

    def test_invalid_filter_type(self):
        generator = EmailReportGenerator()
        params = ReportParams(user_id=self.user1.id, filter_type="invalid_filter")

        with self.assertRaises(ValueError):
            generator.generate_report(params)

    def test_execution_status_distribution(self):
        generator = EmailReportGenerator()

        params = ReportParams(user_id=self.user1.id, filter_type="last_month")
        report = generator.generate_report(params)

        self.assertEqual(report.stats.successful_deliveries, 8)
        self.assertEqual(report.stats.failed_deliveries, 4)
        self.assertEqual(report.stats.total_sent, 12)
