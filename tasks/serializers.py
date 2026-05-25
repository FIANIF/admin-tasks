from rest_framework import serializers
from .models import RegulatedTask, TaskExecution, SystemResource, ServiceStatus, NotificationLog


class RegulatedTaskSerializer(serializers.ModelSerializer):
    assigned_to_names = serializers.StringRelatedField(
        source='assigned_to',
        many=True,
        read_only=True
    )
    created_by_name = serializers.StringRelatedField(
        source='created_by',
        read_only=True
    )

    class Meta:
        model = RegulatedTask
        fields = [
            'id', 'name', 'description', 'task_type', 'schedule',
            'priority', 'command', 'is_active', 'created_at', 'updated_at',
            'created_by_name', 'assigned_to_names', 'notify_emails'
        ]


class TaskExecutionSerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.name', read_only=True)
    task_type = serializers.CharField(source='task.task_type', read_only=True)

    class Meta:
        model = TaskExecution
        fields = [
            'id', 'task', 'task_name', 'task_type', 'status', 'started_at',
            'completed_at', 'duration_seconds', 'stdout', 'stderr', 'exit_code',
            'executed_by', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class SystemResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemResource
        fields = ['id', 'timestamp', 'cpu_percent', 'memory_percent', 'disk_percent', 'disk_free_gb']


class ServiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceStatus
        fields = ['id', 'service_name', 'status', 'last_checked', 'error_message']


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = ['id', 'task_execution', 'recipient_email', 'subject', 'sent_at', 'status', 'error_message']
