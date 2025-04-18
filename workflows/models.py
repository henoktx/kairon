from django.db import models

from users.models import User


class Workflow(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    delay_seconds = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='schedules')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    minute = models.IntegerField(null=True, blank=True)
    hour = models.IntegerField(null=True, blank=True)
    day_of_month = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    day_of_week = models.IntegerField(null=True, blank=True)

    temporal_schedule_id = models.CharField(max_length=100, blank=True)


class Task(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    task_type = models.CharField(
        max_length=20,
        choices=[("email", "Email Sending"), ("report", "Report Generation")]
    )
    retry_attempts = models.PositiveIntegerField(default=5)
    retry_delay = models.PositiveIntegerField(default=15)

    def __str__(self):
        return self.name


class EmailTask(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="email_config")
    recipients = models.TextField(help_text="List of email recipients, separated by commas")
    subject = models.CharField(max_length=200)
    content = models.TextField()
    cc = models.TextField(help_text="List of CC email addresses, separated by commas", blank=True)

    def get_recipients_list(self):
        return [email.strip() for email in self.recipients.split(',') if email.strip()]

    def get_cc_list(self):
        return [email.strip() for email in self.cc.split(',') if email.strip()]

    def __str__(self):
        return self.task.name


class ReportTask(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="report_config")
    filter_type = models.CharField(
        max_length=20,
        choices=[
            ("last_hour", "Last Hour"),
            ("last_day", "Last Day"),
            ("last_week", "Last Week"),
            ("last_month", "Last Month")
        ],
        default="last_hour"
    )

    def __str__(self):
        return self.task.name
    