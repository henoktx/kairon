from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from django.utils import timezone

from executions.models import TaskExecution
from reports.types.report import EmailDeliveryReport, EmailStats, ReportParams
from users.models import User


class EmailReportGenerator:
    @staticmethod
    def _get_date_range(filter_type: str) -> Tuple[datetime, datetime]:
        end_date = timezone.now()

        if filter_type == "last_hour":
            start_date = end_date - timedelta(hours=1)
        elif filter_type == "last_day":
            start_date = end_date - timedelta(days=1)
        elif filter_type == "last_week":
            start_date = end_date - timedelta(weeks=1)
        elif filter_type == "last_month":
            start_date = end_date - timedelta(days=30)
        else:
            raise ValueError(f"Invalid filter type: {filter_type}")

        return start_date, end_date

    def _get_email_stats(self, executions: List[TaskExecution]) -> EmailStats:
        total_sent = len(executions)
        successful = sum(1 for e in executions if e.status == "completed")
        failed = sum(1 for e in executions if e.status == "failed")

        all_recipients = []
        unique_recipients = set()

        for execution in executions:
            email_task = execution.task.email_config
            recipients = email_task.get_recipients_list()
            cc_list = email_task.get_cc_list()

            all_recipients.extend(recipients)
            all_recipients.extend(cc_list)
            unique_recipients.update(recipients)
            unique_recipients.update(cc_list)

        avg_delivery_time = (
            sum(
                e.execution_time() for e in executions if e.execution_time() is not None
            )
            / len([e for e in executions if e.execution_time() is not None])
            if executions
            else 0.0
        )

        return EmailStats(
            total_sent=total_sent,
            successful_deliveries=successful,
            failed_deliveries=failed,
            total_recipients=len(all_recipients),
            unique_recipients=len(unique_recipients),
            average_delivery_time=round(avg_delivery_time, 2),
        )

    def _get_most_common_recipients(
        self, executions: List[TaskExecution], limit: int = 10
    ) -> List[Dict[str, int]]:
        all_recipients = []

        for execution in executions:
            email_task = execution.task.email_config
            recipients = email_task.get_recipients_list()
            cc_list = email_task.get_cc_list()
            all_recipients.extend(recipients)
            all_recipients.extend(cc_list)

        counter = Counter(all_recipients)
        return [
            {"email": email, "count": count}
            for email, count in counter.most_common(limit)
        ]

    def generate_report(self, params: ReportParams) -> EmailDeliveryReport:
        try:
            user = User.objects.get(id=params.user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with id {params.user_id} not found")

        start_date, end_date = self._get_date_range(params.filter_type)

        executions = (
            TaskExecution.objects.filter(
                task__created_by=user,
                task__task_type="email",
                started_at__range=(start_date, end_date),
            )
            .select_related("task__email_config")
            .order_by("-started_at")
        )

        executions_list = list(executions)

        stats = self._get_email_stats(executions_list)
        most_common = self._get_most_common_recipients(executions_list)

        return EmailDeliveryReport(
            user_email=user.email,
            period_start=start_date,
            period_end=end_date,
            stats=stats,
            most_common_recipients=most_common,
        )
