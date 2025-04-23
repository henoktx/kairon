# temporal/tests.py
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from django.test import TestCase
from django.utils import timezone
from temporalio import exceptions

from executions.types.execution import UpdateExecutionParams
from executions.types.task_execution import UpdateTaskExecutionParams
from notifications.types.email import EmailParams
from reports.types.report import ReportParams, EmailDeliveryReport, EmailStats
from temporal.activities import (
    update_task_status_activity,
    update_execution_status_activity,
    send_email_activity,
    generate_report_activity,
)


class TemporalActivitiesTestCase(TestCase):
    def setUp(self):
        self.task_params = UpdateTaskExecutionParams(
            task_execution_id=1, status="completed", error_message=None
        )

        self.execution_params = UpdateExecutionParams(
            execution_id=1, status="completed", error_message=None
        )

        self.email_params = EmailParams(
            subject="Test Email",
            to_email=["test@example.com"],
            content="Test content",
            html_content="<p>Test HTML content</p>",
        )

        self.report_params = ReportParams(user_id=1, filter_type="last_day")

        self.report_result = EmailDeliveryReport(
            user_email="user@example.com",
            period_start=timezone.now(),
            period_end=timezone.now(),
            stats=EmailStats(
                total_sent=10,
                successful_deliveries=8,
                failed_deliveries=2,
                total_recipients=15,
                unique_recipients=5,
                average_delivery_time=1.5,
            ),
            most_common_recipients=[{"email": "common@example.com", "count": 5}],
        )

    @patch("temporal.activities.update_task_execution_status")
    @patch("temporal.activities.sync_to_async")
    def test_update_task_status_activity_success(
        self, mock_sync_to_async, mock_update_task
    ):
        async_result = AsyncMock()
        mock_sync_to_async.return_value = async_result

        async def run_test():
            await update_task_status_activity(self.task_params)

        asyncio.run(run_test())

        mock_sync_to_async.assert_called_once_with(mock_update_task)
        async_result.assert_called_once_with(self.task_params)

    @patch("temporal.activities.update_task_execution_status")
    @patch("temporal.activities.sync_to_async")
    def test_update_task_status_activity_error(
        self, mock_sync_to_async, mock_update_task
    ):
        async_mock = AsyncMock()
        async_mock.side_effect = ValueError("Erro de teste")
        mock_sync_to_async.return_value = async_mock

        async def run_test():
            with self.assertRaises(exceptions.ApplicationError):
                await update_task_status_activity(self.task_params)

        asyncio.run(run_test())

    @patch("temporal.activities.update_execution_status")
    @patch("temporal.activities.sync_to_async")
    def test_update_execution_status_activity_success(
        self, mock_sync_to_async, mock_update_execution
    ):
        async_result = AsyncMock()
        mock_sync_to_async.return_value = async_result

        async def run_test():
            await update_execution_status_activity(self.execution_params)

        asyncio.run(run_test())

        mock_sync_to_async.assert_called_once_with(mock_update_execution)
        async_result.assert_called_once_with(self.execution_params)

    @patch("temporal.activities.update_execution_status")
    @patch("temporal.activities.sync_to_async")
    def test_update_execution_status_activity_error(
        self, mock_sync_to_async, mock_update_execution
    ):
        async_mock = AsyncMock()
        async_mock.side_effect = ValueError("Erro de teste")
        mock_sync_to_async.return_value = async_mock

        async def run_test():
            with self.assertRaises(exceptions.ApplicationError):
                await update_execution_status_activity(self.execution_params)

        asyncio.run(run_test())

    @patch("temporal.activities.MailerSendService")
    @patch("temporal.activities.sync_to_async")
    def test_send_email_activity_success(
        self, mock_sync_to_async, mock_mailer_service_class
    ):
        mock_mailer = MagicMock()
        mock_mailer_service_class.return_value = mock_mailer

        async_result = AsyncMock()
        mock_sync_to_async.return_value = async_result

        async def run_test():
            await send_email_activity(self.email_params)

        asyncio.run(run_test())

        mock_mailer_service_class.assert_called_once()
        mock_sync_to_async.assert_called_once()
        async_result.assert_called_once_with(self.email_params)

    @patch("temporal.activities.MailerSendService")
    @patch("temporal.activities.sync_to_async")
    def test_send_email_activity_error(
        self, mock_sync_to_async, mock_mailer_service_class
    ):
        mock_mailer = MagicMock()
        mock_mailer_service_class.return_value = mock_mailer

        async_mock = AsyncMock()
        async_mock.side_effect = ValueError("Erro de teste")
        mock_sync_to_async.return_value = async_mock

        async def run_test():
            with self.assertRaises(exceptions.ApplicationError):
                await send_email_activity(self.email_params)

        asyncio.run(run_test())

    @patch("temporal.activities.EmailReportGenerator")
    @patch("temporal.activities.format_report_as_html")
    @patch("temporal.activities.sync_to_async")
    def test_generate_report_activity_success(
        self, mock_sync_to_async, mock_format_html, mock_report_generator_class
    ):
        mock_generator = MagicMock()
        mock_report_generator_class.return_value = mock_generator

        async_mock = AsyncMock(return_value=self.report_result)
        mock_sync_to_async.return_value = async_mock

        mock_format_html.return_value = "<html>Report content</html>"

        async def run_test():
            result = await generate_report_activity(self.report_params)
            self.assertEqual(result.subject, "Envio de relatório de emails")
            self.assertEqual(result.to_email, ["user@example.com"])
            self.assertEqual(result.html_content, "<html>Report content</html>")

        asyncio.run(run_test())

        mock_report_generator_class.assert_called_once()
        mock_sync_to_async.assert_called_once()
        mock_format_html.assert_called_once_with(self.report_result)

    @patch("temporal.activities.EmailReportGenerator")
    @patch("temporal.activities.sync_to_async")
    def test_generate_report_activity_error(
        self, mock_sync_to_async, mock_report_generator_class
    ):
        mock_generator = MagicMock()
        mock_report_generator_class.return_value = mock_generator

        async_mock = AsyncMock()
        async_mock.side_effect = ValueError("Erro de teste")
        mock_sync_to_async.return_value = async_mock

        async def run_test():
            with self.assertRaises(exceptions.ApplicationError):
                await generate_report_activity(self.report_params)

        asyncio.run(run_test())
