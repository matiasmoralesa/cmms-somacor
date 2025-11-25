from rest_framework import serializers
from .models import AssetStatus, AssetStatusHistory
from apps.assets.models import Asset


class AssetStatusSerializer(serializers.ModelSerializer):
    """Serializer for AssetStatus model"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_type_display', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AssetStatus
        fields = [
            'id', 'asset', 'asset_name', 'asset_code',
            'status_type', 'status_display',
            'odometer_reading', 'fuel_level', 'condition_notes',
            'location', 'location_name',
            'reported_by', 'reported_by_name', 'reported_at'
        ]
        read_only_fields = ['id', 'reported_by', 'reported_at']
    
    def validate_fuel_level(self, value):
        """Validate fuel level is between 0 and 100"""
        if value is not None:
            if value < 0 or value > 100:
                raise serializers.ValidationError("El nivel de combustible debe estar entre 0 y 100")
        return value
    
    def validate_asset(self, value):
        """Validate that asset exists and is active"""
        if not value.is_active:
            raise serializers.ValidationError("No se puede actualizar el estado de un activo inactivo")
        return value


class AssetStatusCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating asset status updates"""
    
    class Meta:
        model = AssetStatus
        fields = [
            'asset', 'status_type', 'odometer_reading',
            'fuel_level', 'condition_notes', 'location'
        ]
    
    def validate_fuel_level(self, value):
        if value is not None:
            if value < 0 or value > 100:
                raise serializers.ValidationError("El nivel de combustible debe estar entre 0 y 100")
        return value
    
    def validate_asset(self, value):
        """Validate asset access based on user role"""
        user = self.context['request'].user
        
        # ADMIN and SUPERVISOR can update any asset
        if user.can_view_all_resources():
            return value
        
        # OPERADOR can only update assigned assets
        if user.is_operador():
            # Check if user has active work orders for this asset
            from apps.work_orders.models import WorkOrder
            has_assignment = WorkOrder.objects.filter(
                asset=value,
                assigned_to=user,
                status__in=['ASSIGNED', 'IN_PROGRESS']
            ).exists()
            
            if not has_assignment:
                raise serializers.ValidationError(
                    "No tienes permisos para actualizar el estado de este activo. "
                    "Solo puedes actualizar activos asignados a ti."
                )
        
        return value


class AssetStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for AssetStatusHistory model"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = AssetStatusHistory
        fields = [
            'id', 'asset', 'asset_name',
            'previous_status', 'new_status',
            'previous_odometer', 'new_odometer',
            'changed_by', 'changed_by_name',
            'changed_at', 'change_reason'
        ]
        read_only_fields = ['id', 'changed_at']


class AssetStatusListSerializer(serializers.ModelSerializer):
    """Simplified serializer for status lists"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    status_display = serializers.CharField(source='get_status_type_display', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    
    class Meta:
        model = AssetStatus
        fields = [
            'id', 'asset', 'asset_name',
            'status_type', 'status_display',
            'odometer_reading', 'fuel_level',
            'reported_by_name', 'reported_at'
        ]
