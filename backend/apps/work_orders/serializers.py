"""Serializers for work orders"""
from rest_framework import serializers
from django.utils import timezone
from .models import WorkOrder


class WorkOrderSerializer(serializers.ModelSerializer):
    work_order_type_display = serializers.CharField(source='get_work_order_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Use SerializerMethodField to safely handle null assets
    asset_name = serializers.SerializerMethodField()
    asset_code = serializers.SerializerMethodField()
    
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = WorkOrder
        fields = [
            'id', 'work_order_number', 'title', 'description',
            'asset', 'asset_name', 'asset_code',
            'work_order_type', 'work_order_type_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name',
            'scheduled_date', 'started_at', 'completed_at',
            'estimated_hours', 'actual_hours', 'completion_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'work_order_number', 'created_by',
            'started_at', 'completed_at', 'created_at', 'updated_at'
        ]
    
    def get_asset_name(self, obj):
        """
        Safely get asset name.
        Returns None if asset is not assigned to avoid null reference errors.
        """
        return obj.asset.name if obj.asset else None
    
    def get_asset_code(self, obj):
        """
        Safely get asset code.
        Returns None if asset is not assigned to avoid null reference errors.
        """
        return obj.asset.asset_code if obj.asset else None


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = [
            'title', 'description', 'asset', 'work_order_type',
            'priority', 'assigned_to', 'scheduled_date', 'estimated_hours'
        ]
    
    def validate(self, data):
        """
        Validate work order data.
        Certain work order types require an asset to be assigned.
        """
        asset = data.get('asset')
        work_order_type = data.get('work_order_type')
        
        # PREVENTIVE and PREDICTIVE work orders require an asset
        if work_order_type in [WorkOrder.TYPE_PREVENTIVE, WorkOrder.TYPE_PREDICTIVE]:
            if not asset:
                raise serializers.ValidationError({
                    'asset': f'Las órdenes de tipo {dict(WorkOrder.TYPE_CHOICES).get(work_order_type)} requieren un equipo asignado'
                })
        
        # Validate asset exists if provided
        if asset:
            from apps.assets.models import Asset
            try:
                Asset.objects.get(id=asset.id)
            except Asset.DoesNotExist:
                raise serializers.ValidationError({
                    'asset': 'El equipo seleccionado no existe'
                })
        
        return data


class WorkOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = [
            'title', 'description', 'work_order_type', 'priority',
            'assigned_to', 'scheduled_date', 'estimated_hours', 'status'
        ]


class WorkOrderCompleteSerializer(serializers.Serializer):
    actual_hours = serializers.DecimalField(max_digits=5, decimal_places=2, required=True)
    completion_notes = serializers.CharField(required=True)
    
    def validate_actual_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError('Las horas trabajadas deben ser mayor a 0')
        return value
    
    def validate_completion_notes(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Las notas deben tener al menos 10 caracteres')
        return value


class WorkOrderStatusChangeSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=WorkOrder.STATUS_CHOICES, required=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        instance = self.context.get('instance')
        if not instance:
            return value
        
        # Validate status transitions
        current_status = instance.status
        
        # Can't go back to PENDING once assigned
        if current_status != WorkOrder.STATUS_PENDING and value == WorkOrder.STATUS_PENDING:
            raise serializers.ValidationError('No se puede volver a estado PENDIENTE')
        
        # Can't skip ASSIGNED
        if current_status == WorkOrder.STATUS_PENDING and value == WorkOrder.STATUS_IN_PROGRESS:
            if not instance.assigned_to:
                raise serializers.ValidationError('Debe asignar la OT antes de iniciarla')
        
        return value
