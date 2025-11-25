"""Serializers for inventory"""
from rest_framework import serializers
from .models import SparePart, StockMovement


class SparePartSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.SerializerMethodField()
    stock_percentage = serializers.SerializerMethodField()
    compatible_assets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SparePart
        fields = [
            'id', 'part_number', 'name', 'description', 'category',
            'quantity', 'minimum_stock', 'unit_cost', 'location', 'supplier',
            'compatible_assets', 'is_low_stock', 'stock_percentage',
            'compatible_assets_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
    
    def get_stock_percentage(self, obj):
        return round(obj.stock_percentage(), 2)
    
    def get_compatible_assets_count(self, obj):
        return obj.compatible_assets.count()


class StockMovementSerializer(serializers.ModelSerializer):
    spare_part_name = serializers.CharField(source='spare_part.name', read_only=True)
    spare_part_number = serializers.CharField(source='spare_part.part_number', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    work_order_number = serializers.CharField(source='work_order.work_order_number', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'spare_part', 'spare_part_name', 'spare_part_number',
            'movement_type', 'movement_type_display', 'quantity',
            'work_order', 'work_order_number', 'performed_by', 'performed_by_name',
            'notes', 'stock_before', 'stock_after', 'created_at'
        ]
        read_only_fields = ['id', 'stock_before', 'stock_after', 'created_at']


class StockAdjustmentSerializer(serializers.Serializer):
    movement_type = serializers.ChoiceField(choices=StockMovement.MOVEMENT_TYPE_CHOICES)
    quantity = serializers.IntegerField()
    work_order = serializers.UUIDField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError('La cantidad debe ser diferente de 0')
        return value
