from rest_framework import serializers

from .models import Workflow, Task, Schedule, EmailTask, ReportTask
from .services.create_workflow import create_workflow


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
            "maximum_attempts",
            "initial_interval",
            "back_off",
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["email_config"] is None:
            representation.pop("email_config")
        if representation["report_config"] is None:
            representation.pop("report_config")

        return representation


class ScheduleSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ["minute", "hour", "day_of_month", "day_of_week"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {
            key: value for key, value in representation.items() if value is not None
        }


class WorkflowSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)
    schedule = ScheduleSpecSerializer(required=False)

    class Meta:
        model = Workflow
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "delay_minutes",
            "tasks",
            "schedule",
        ]
        read_only_fields = ["created_by", "created_at", "id"]

    def create(self, validated_data):
        tasks_data = validated_data.pop("tasks")
        schedule_data = validated_data.pop("schedule", None)
        return create_workflow(validated_data, tasks_data, schedule_data)


class WorkflowSimpleSerializer(serializers.ModelSerializer):
    schedule = ScheduleSpecSerializer()

    class Meta:
        model = Workflow
        fields = ["id", "name", "created_at", "schedule"]
        read_only_fields = fields


class TaskSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name", "task_type"]
        read_only_fields = fields
