from rest_framework import serializers

from workflows.serializers import WorkflowSimpleSerializer, TaskSimpleSerializer
from .models import Execution, TaskExecution


class TaskExecutionSerializer(serializers.ModelSerializer):
    task = TaskSimpleSerializer(read_only=True)
    execution_time = serializers.SerializerMethodField()

    class Meta:
        model = TaskExecution
        fields = [
            "id",
            "task",
            "started_at",
            "completed_at",
            "status",
            "error_message",
            "execution_time",
        ]
        read_only_fields = fields

    def get_execution_time(self, obj):
        return obj.execution_time()


class ExecutionSerializer(serializers.ModelSerializer):
    workflow = WorkflowSimpleSerializer(read_only=True)
    task_executions = TaskExecutionSerializer(many=True, read_only=True)
    execution_time = serializers.SerializerMethodField()

    class Meta:
        model = Execution
        fields = [
            "id",
            "workflow",
            "created_by",
            "started_at",
            "completed_at",
            "status",
            "error_message",
            "task_executions",
            "execution_time",
        ]
        read_only_fields = fields

    def get_execution_time(self, obj):
        return obj.execution_time()


class TaskExecutionDetailSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source="task.name", read_only=True)
    task_type = serializers.CharField(source="task.task_type", read_only=True)
    execution_workflow = serializers.CharField(
        source="execution.workflow.name", read_only=True
    )
    execution_time = serializers.SerializerMethodField()

    class Meta:
        model = TaskExecution
        fields = [
            "id",
            "task_name",
            "task_type",
            "execution_workflow",
            "started_at",
            "completed_at",
            "status",
            "error_message",
            "execution_time",
        ]
        read_only_fields = fields

    def get_execution_time(self, obj):
        return obj.execution_time()
