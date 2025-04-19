from django.db import models

from workflows.models import Workflow, Task
from users.models import User


class Execution(models.Model):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="executions")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("canceled", "Canceled"),
            ("terminated", "Terminated")
        ],
        default="running"
    )

    temporal_workflow_id = models.CharField(max_length=100, blank=True)
    temporal_run_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Execution {self.id} - {self.workflow.name} ({self.status})"

    def execution_time(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TaskExecution(models.Model):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE, related_name="task_executions")
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="running"
    )

    retry_count = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    temporal_activity_id = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["execution", "task__order"]

    def __str__(self):
        return f"Task {self.task.name} ({self.status})"

    def execution_time(self):
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None