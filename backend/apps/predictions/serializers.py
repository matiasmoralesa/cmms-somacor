"""
Serializers for predictions app
"""
from rest_framework import serializers
from .models import FailurePrediction, Alert


class FailurePredictionSerializer(serializers.ModelSerializer):
    """Serializer for FailurePrediction model"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)

    class Meta:
        model = FailurePrediction
        fields = [
            'id',
            'asset',
            'asset_name',
            'asset_code',
            'prediction_date',
            'failure_probability',
            'predicted_failure_date',
            'confidence_score',
            'model_version',
            'input_features',
            'recommendations',
            'risk_level',
            'risk_level_display',
            'created_at',
        ]
        read_only_fields = ['id', 'prediction_date', 'created_at', 'risk_level']


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id',
            'alert_type',
            'alert_type_display',
            'severity',
            'severity_display',
            'title',
            'message',
            'asset',
            'asset_name',
            'work_order',
            'prediction',
            'is_read',
            'is_resolved',
            'resolved_by',
            'resolved_by_name',
            'resolved_at',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']


class AlertActionSerializer(serializers.Serializer):
    """Serializer for alert actions"""
    action = serializers.ChoiceField(choices=['mark_read', 'resolve'])
