"""
Serializers for notifications app
"""
from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Related object names
    work_order_number = serializers.CharField(source='work_order.work_order_number', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'notification_type_display',
            'priority', 'priority_display', 'title', 'message',
            'work_order', 'work_order_number', 'asset', 'asset_name',
            'prediction', 'data', 'is_read', 'read_at',
            'pubsub_message_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'pubsub_message_id']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'notification_type', 'priority', 'title', 'message',
            'work_order', 'asset', 'prediction', 'data'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'notification_type_display',
            'in_app_enabled', 'email_enabled', 'push_enabled', 'telegram_enabled',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for bulk notification creation"""
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, default='MEDIUM')
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    data = serializers.JSONField(required=False, default=dict)
