"""Serializers for Assets app"""
from rest_framework import serializers
from .models import Asset, Location, AssetDocument


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""
    asset_count = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'address', 'city', 'region', 
            'coordinates', 'description', 'is_active',
            'created_at', 'updated_at', 'asset_count', 'can_delete'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'asset_count', 'can_delete']
    
    def get_asset_count(self, obj):
        """Get count of assets in this location"""
        return obj.assets.count() if hasattr(obj, 'assets') else 0
    
    def get_can_delete(self, obj):
        """Check if location can be deleted"""
        return obj.can_be_deleted()
    
    def validate_name(self, value):
        """Validate that location name is unique"""
        instance = self.instance
        if Location.objects.filter(name=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Ya existe una ubicación con este nombre.")
        return value
    
    def validate_coordinates(self, value):
        """Validate coordinates format"""
        if value:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Las coordenadas deben ser un objeto JSON.")
            if 'lat' not in value or 'lng' not in value:
                raise serializers.ValidationError("Las coordenadas deben incluir 'lat' y 'lng'.")
            try:
                lat = float(value['lat'])
                lng = float(value['lng'])
                if not (-90 <= lat <= 90):
                    raise serializers.ValidationError("La latitud debe estar entre -90 y 90.")
                if not (-180 <= lng <= 180):
                    raise serializers.ValidationError("La longitud debe estar entre -180 y 180.")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Las coordenadas deben ser números válidos.")
        return value


class LocationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for location lists"""
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'region', 'is_active', 'asset_count']
    
    def get_asset_count(self, obj):
        return obj.assets.count() if hasattr(obj, 'assets') else 0


class AssetDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Asset Documents"""
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetDocument
        fields = ['id', 'asset', 'document_type', 'file_url', 'file_name', 
                  'file_size', 'description', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return f"{obj.uploaded_by.first_name} {obj.uploaded_by.last_name}"
        return None


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)
    checklist_code = serializers.CharField(source='get_checklist_code', read_only=True)
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_code', 'vehicle_type', 'vehicle_type_display',
            'location', 'location_name', 'manufacturer', 'model', 'serial_number',
            'license_plate', 'installation_date', 'last_maintenance_date',
            'status', 'status_display', 'criticality', 'criticality_display',
            'specifications', 'is_active', 'created_by', 'created_by_name',
            'checklist_code', 'documents_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_documents_count(self, obj):
        return obj.documents.count()


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for asset lists"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_code', 'vehicle_type', 'vehicle_type_display',
            'location_name', 'status', 'status_display', 'criticality',
            'manufacturer', 'model', 'license_plate'
        ]


class AssetStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating asset status (for operators)"""
    status = serializers.ChoiceField(choices=Asset.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Validate status transition"""
        # Add any business logic for valid status transitions
        return value
