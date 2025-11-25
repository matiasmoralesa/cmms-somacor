"""
Serializers for core app
"""
from rest_framework import serializers
from .models import Webhook, WebhookDelivery
import secrets


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for Webhook model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'secret', 'is_active',
            'max_retries', 'retry_delay_seconds',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'success_rate', 'last_delivery_at', 'last_delivery_status',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'secret', 'total_deliveries', 'successful_deliveries',
            'failed_deliveries', 'last_delivery_at', 'last_delivery_status',
            'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        if obj.total_deliveries == 0:
            return 0
        return round((obj.successful_deliveries / obj.total_deliveries) * 100, 2)
    
    def create(self, validated_data):
        """Generate secret on creation"""
        validated_data['secret'] = secrets.token_hex(32)
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_events(self, value):
        """Validate event types"""
        valid_events = [choice[0] for choice in Webhook.EVENT_CHOICES]
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(f"Evento inválido: {event}")
        return value


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery model"""
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    
    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event_type', 'payload',
            'status', 'http_status_code', 'response_body', 'error_message',
            'attempt_count', 'next_retry_at',
            'created_at', 'delivered_at', 'duration_ms'
        ]
        read_only_fields = ['id', 'created_at']


class WebhookTestSerializer(serializers.Serializer):
    """Serializer for testing webhook"""
    event_type = serializers.ChoiceField(choices=Webhook.EVENT_CHOICES)
    test_payload = serializers.JSONField(required=False)
