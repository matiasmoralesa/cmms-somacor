"""
Serializers for configuration app
"""
from rest_framework import serializers
from .models import AssetCategory, Location, Priority, WorkOrderType, SystemParameter, AuditLog


class AssetCategorySerializer(serializers.ModelSerializer):
    """Serializer for AssetCategory model"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = AssetCategory
        fields = [
            'id', 'name', 'code', 'description', 'parent', 'parent_name',
            'is_active', 'is_system', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'code', 'description', 'address', 'city', 'state',
            'country', 'latitude', 'longitude', 'is_active', 'is_system',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']


class PrioritySerializer(serializers.ModelSerializer):
    """Serializer for Priority model"""
    
    class Meta:
        model = Priority
        fields = [
            'id', 'name', 'code', 'description', 'level', 'color',
            'response_time_hours', 'is_active', 'is_system',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']


class WorkOrderTypeSerializer(serializers.ModelSerializer):
    """Serializer for WorkOrderType model"""
    default_priority_name = serializers.CharField(source='default_priority.name', read_only=True)
    
    class Meta:
        model = WorkOrderType
        fields = [
            'id', 'name', 'code', 'description', 'requires_approval',
            'default_priority', 'default_priority_name', 'estimated_hours',
            'is_active', 'is_system', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system']


class SystemParameterSerializer(serializers.ModelSerializer):
    """Serializer for SystemParameter model"""
    
    class Meta:
        model = SystemParameter
        fields = [
            'id', 'key', 'value', 'data_type', 'description',
            'is_sensitive', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Hide sensitive values"""
        data = super().to_representation(instance)
        if instance.is_sensitive:
            data['value'] = '***HIDDEN***'
        return data


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'model_name', 'object_id', 'object_repr', 'action',
            'changes', 'user', 'user_name', 'timestamp', 'ip_address'
        ]
        read_only_fields = ['id', 'timestamp']
