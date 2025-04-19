from rest_framework import serializers
from .models import Execution, TaskExecution
from workflows.serializers import WorkflowSerializer, TaskSerializer


class TaskExecutionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    execution_time = serializers.SerializerMethodField()

    class Meta:
        model = TaskExecution
        fields = [
            "id",
            "task",
            "started_at",
            "completed_at",
            "status",
            "retry_count",
            "next_retry_at",
            "temporal_activity_id",
            "error_message",
            "execution_time",
        ]
        read_only_fields = fields

    def get_execution_time(self, obj):
        return obj.execution_time()


class ExecutionSerializer(serializers.ModelSerializer):
    workflow = WorkflowSerializer(read_only=True)
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
            "retry_count",
            "next_retry_at",
            "error_message",
            "execution_time",
        ]
        read_only_fields = fields

    def get_execution_time(self, obj):
        return obj.execution_time()
