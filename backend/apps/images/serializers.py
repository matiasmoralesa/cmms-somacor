"""
Serializers for image processing models.
"""
from rest_framework import serializers
from apps.images.models import (
    InspectionPhoto,
    ImageAnalysisResult,
    VisualAnomaly,
    MeterReading,
    DamageReport
)
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.checklists.models import ChecklistResponse


class InspectionPhotoUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading inspection photos.
    Handles file upload, validation, and metadata extraction.
    """
    image = serializers.ImageField(required=True)
    asset_id = serializers.UUIDField(required=True)
    work_order_id = serializers.UUIDField(required=False, allow_null=True)
    checklist_response_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_asset_id(self, value):
        """Validate that asset exists."""
        try:
            Asset.objects.get(id=value)
        except Asset.DoesNotExist:
            raise serializers.ValidationError("Asset not found")
        return value
    
    def validate_work_order_id(self, value):
        """Validate that work order exists if provided."""
        if value:
            try:
                WorkOrder.objects.get(id=value)
            except WorkOrder.DoesNotExist:
                raise serializers.ValidationError("Work order not found")
        return value
    
    def validate_checklist_response_id(self, value):
        """Validate that checklist response exists if provided."""
        if value:
            try:
                ChecklistResponse.objects.get(id=value)
            except ChecklistResponse.DoesNotExist:
                raise serializers.ValidationError("Checklist response not found")
        return value


class InspectionPhotoSerializer(serializers.ModelSerializer):
    """Serializer for InspectionPhoto model."""
    
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    has_gps = serializers.SerializerMethodField()
    gps_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = InspectionPhoto
        fields = [
            'id', 'asset', 'asset_name', 'asset_code',
            'checklist_response', 'work_order',
            'original_url', 'thumbnail_url',
            'file_size', 'width', 'height', 'format',
            'captured_at', 'gps_latitude', 'gps_longitude',
            'gps_altitude', 'compass_heading', 'device_info',
            'has_gps', 'gps_coordinates',
            'processing_status', 'processed_at', 'processing_error',
            'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'processing_status', 'processed_at', 'processing_error',
            'created_at', 'updated_at'
        ]
    
    def get_has_gps(self, obj):
        """Check if photo has GPS data."""
        return obj.has_gps_data()
    
    def get_gps_coordinates(self, obj):
        """Get GPS coordinates as tuple."""
        coords = obj.get_gps_coordinates()
        if coords:
            return {'latitude': coords[0], 'longitude': coords[1]}
        return None


class ImageAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for ImageAnalysisResult model."""
    
    photo_id = serializers.UUIDField(source='photo.id', read_only=True)
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = ImageAnalysisResult
        fields = [
            'id', 'photo', 'photo_id',
            'labels', 'detected_objects', 'text_annotations',
            'dominant_colors', 'safe_search',
            'anomalies_detected', 'anomaly_confidence',
            'damage_type', 'damage_severity', 'damage_confidence',
            'processing_time_ms', 'model_version', 'vision_ai_used',
            'cached_result', 'cache_expires_at',
            'summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_summary(self, obj):
        """Get human-readable summary."""
        return obj.get_summary()


class VisualAnomalySerializer(serializers.ModelSerializer):
    """Serializer for VisualAnomaly model."""
    
    photo_id = serializers.UUIDField(source='photo.id', read_only=True)
    asset_name = serializers.CharField(source='photo.asset.name', read_only=True)
    anomaly_type_display = serializers.CharField(source='get_anomaly_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    is_critical = serializers.SerializerMethodField()
    needs_action = serializers.SerializerMethodField()
    
    class Meta:
        model = VisualAnomaly
        fields = [
            'id', 'photo', 'photo_id', 'asset_name',
            'analysis_result',
            'anomaly_type', 'anomaly_type_display',
            'severity', 'severity_display',
            'confidence', 'bounding_box', 'description',
            'confirmed_by_user', 'user_feedback', 'feedback_by', 'feedback_at',
            'work_order_created', 'alert_sent', 'alert_sent_at',
            'is_critical', 'needs_action',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'alert_sent', 'alert_sent_at',
            'created_at', 'updated_at'
        ]
    
    def get_is_critical(self, obj):
        """Check if anomaly is critical."""
        return obj.is_critical()
    
    def get_needs_action(self, obj):
        """Check if anomaly needs work order."""
        return obj.needs_work_order()


class MeterReadingSerializer(serializers.ModelSerializer):
    """Serializer for MeterReading model."""
    
    photo_id = serializers.UUIDField(source='photo.id', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    reading_type_display = serializers.CharField(source='get_reading_type_display', read_only=True)
    is_within_range = serializers.SerializerMethodField()
    
    class Meta:
        model = MeterReading
        fields = [
            'id', 'photo', 'photo_id', 'asset', 'asset_name',
            'reading_type', 'reading_type_display',
            'value', 'unit',
            'confidence', 'text_detected', 'bounding_box',
            'is_valid', 'is_outlier', 'validation_notes',
            'validated_by', 'validated_at',
            'previous_reading', 'expected_range_min', 'expected_range_max',
            'is_within_range',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'confidence', 'text_detected', 'bounding_box',
            'created_at', 'updated_at'
        ]
    
    def get_is_within_range(self, obj):
        """Check if reading is within expected range."""
        return obj.is_within_expected_range()


class DamageReportSerializer(serializers.ModelSerializer):
    """Serializer for DamageReport model."""
    
    photo_id = serializers.UUIDField(source='photo.id', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    damage_type_display = serializers.CharField(source='get_damage_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_critical = serializers.SerializerMethodField()
    needs_action = serializers.SerializerMethodField()
    
    class Meta:
        model = DamageReport
        fields = [
            'id', 'photo', 'photo_id', 'asset', 'asset_name',
            'damage_type', 'damage_type_display',
            'severity', 'severity_display',
            'confidence',
            'auto_generated_description', 'user_notes', 'maintenance_recommendation',
            'work_order', 'maintenance_plan_updated',
            'status', 'status_display',
            'resolved_at', 'resolved_by',
            'is_critical', 'needs_action',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'auto_generated_description', 'confidence',
            'created_at', 'updated_at'
        ]
    
    def get_is_critical(self, obj):
        """Check if damage is critical."""
        return obj.is_critical()
    
    def get_needs_action(self, obj):
        """Check if damage needs immediate action."""
        return obj.needs_immediate_action()


class InspectionPhotoDetailSerializer(InspectionPhotoSerializer):
    """
    Detailed serializer for InspectionPhoto with nested analysis results.
    """
    analysis_result = ImageAnalysisResultSerializer(read_only=True)
    anomalies = VisualAnomalySerializer(many=True, read_only=True)
    meter_readings = MeterReadingSerializer(many=True, read_only=True)
    damage_reports = DamageReportSerializer(many=True, read_only=True)
    
    class Meta(InspectionPhotoSerializer.Meta):
        fields = InspectionPhotoSerializer.Meta.fields + [
            'analysis_result', 'anomalies', 'meter_readings', 'damage_reports'
        ]
