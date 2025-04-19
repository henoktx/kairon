from rest_framework import serializers
from .models import Workflow, Task, Schedule, EmailTask, ReportTask


class EmailTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTask
        fields = ["recipients", "subject", "content", "cc"]


class ReportTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTask
        fields = ["filter_type"]


class TaskSerializer(serializers.ModelSerializer):
    email_config = EmailTaskSerializer(required=False)
    report_config = ReportTaskSerializer(required=False)

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "order",
            "task_type",
            "retry_attempts",
            "retry_delay",
            "email_config",
            "report_config",
        ]

    def validate(self, data):
        task_type = data.get("task_type")
        email_config = data.get("email_config")
        report_config = data.get("report_config")

        if task_type == "email" and not email_config:
            raise serializers.ValidationError(
                "Email configuration is required for email tasks"
            )
        elif task_type == "report" and not report_config:
            raise serializers.ValidationError(
                "Report configuration is required for report tasks"
            )

        return data


class ScheduleSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["minute", "hour", "day_of_month", "month", "day_of_week"]


class WorkflowSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    spec = ScheduleSpecSerializer(source="schedules", required=False)

    class Meta:
        model = Workflow
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "delay_seconds",
            "tasks",
            "spec",
        ]
        read_only_fields = ["created_by", "created_at", "id"]

    def create(self, validated_data):
        tasks_data = validated_data.pop("tasks")
        schedule_data = validated_data.pop("schedules", None)

        workflow = Workflow.objects.create(**validated_data)

        for task_data in tasks_data:
            email_config = task_data.pop("email_config", None)
            report_config = task_data.pop("report_config", None)

            task = Task.objects.create(workflow=workflow, **task_data)

            if email_config:
                EmailTask.objects.create(task=task, **email_config)
            elif report_config:
                ReportTask.objects.create(task=task, **report_config)

        if schedule_data:
            Schedule.objects.create(
                workflow=workflow,
                created_by=validated_data["created_by"],
                **schedule_data,
            )

        return workflow
