"""Serializers for checklists"""
from rest_framework import serializers
from .models import ChecklistTemplate, ChecklistResponse
from apps.assets.models import Asset


class ChecklistTemplateSerializer(serializers.ModelSerializer):
    vehicle_type_display = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChecklistTemplate
        fields = [
            'id', 'code', 'name', 'vehicle_type', 'vehicle_type_display',
            'description', 'items', 'is_system_template', 'passing_score',
            'item_count', 'response_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_vehicle_type_display(self, obj):
        vehicle_types = dict(Asset.VEHICLE_TYPE_CHOICES)
        return vehicle_types.get(obj.vehicle_type, obj.vehicle_type)
    
    def get_item_count(self, obj):
        return len(obj.items) if obj.items else 0
    
    def get_response_count(self, obj):
        return obj.responses.count()


class ChecklistResponseSerializer(serializers.ModelSerializer):
    template_code = serializers.CharField(source='template.code', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    work_order_number = serializers.CharField(source='work_order.work_order_number', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ChecklistResponse
        fields = [
            'id', 'template', 'template_code', 'template_name',
            'work_order', 'work_order_number', 'asset', 'asset_name', 'asset_code',
            'responses', 'score', 'passed', 'pdf_url', 'signature_url',
            'completed_by', 'completed_by_name', 'completed_at',
            'operator_name', 'shift', 'odometer_reading'
        ]
        read_only_fields = ['id', 'score', 'passed', 'completed_by', 'completed_at']


class ChecklistResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistResponse
        fields = [
            'template', 'work_order', 'asset', 'responses',
            'signature_url', 'operator_name', 'shift', 'odometer_reading'
        ]
    
    def validate(self, attrs):
        """Validate checklist response"""
        template = attrs.get('template')
        asset = attrs.get('asset')
        
        # Validate asset vehicle_type matches template
        if template and asset:
            if asset.vehicle_type != template.vehicle_type:
                raise serializers.ValidationError({
                    'template': f'Esta plantilla es para {template.vehicle_type}, '
                               f'pero el activo es {asset.vehicle_type}'
                })
        
        # Validate responses match template items
        responses = attrs.get('responses', [])
        template_items = template.items if template else []
        
        if len(responses) != len(template_items):
            raise serializers.ValidationError({
                'responses': f'Se esperan {len(template_items)} respuestas, '
                            f'pero se recibieron {len(responses)}'
            })
        
        # Validate response structure
        for idx, response in enumerate(responses):
            if 'item_order' not in response:
                raise serializers.ValidationError({
                    'responses': f'Respuesta {idx + 1} debe incluir "item_order"'
                })
            if 'response' not in response:
                raise serializers.ValidationError({
                    'responses': f'Respuesta {idx + 1} debe incluir "response"'
                })
            
            # Validate response value
            valid_responses = ['yes', 'no', 'na']
            if response['response'] not in valid_responses:
                raise serializers.ValidationError({
                    'responses': f'Respuesta {idx + 1} debe ser una de: {", ".join(valid_responses)}'
                })
        
        return attrs
