"""
Views for configuration app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError
from .models import AssetCategory, Location, Priority, WorkOrderType, SystemParameter, AuditLog
from .serializers import (
    AssetCategorySerializer,
    LocationSerializer,
    PrioritySerializer,
    WorkOrderTypeSerializer,
    SystemParameterSerializer,
    AuditLogSerializer
)
import logging

logger = logging.getLogger(__name__)


class BaseConfigViewSet(viewsets.ModelViewSet):
    """Base viewset for configuration models"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Set created_by and log change"""
        instance = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        AuditLog.log_change(instance, 'CREATE', self.request.user, request=self.request)
    
    def perform_update(self, serializer):
        """Set updated_by and log change"""
        old_instance = self.get_object()
        old_data = self.get_serializer(old_instance).data
        
        instance = serializer.save(updated_by=self.request.user)
        
        new_data = self.get_serializer(instance).data
        changes = {k: {'old': old_data[k], 'new': new_data[k]} 
                   for k in old_data if old_data[k] != new_data[k]}
        
        AuditLog.log_change(instance, 'UPDATE', self.request.user, changes, self.request)
    
    def perform_destroy(self, instance):
        """Log deletion"""
        try:
            AuditLog.log_change(instance, 'DELETE', self.request.user, request=self.request)
            instance.delete()
        except ValidationError as e:
            raise ValidationError(str(e))


class AssetCategoryViewSet(BaseConfigViewSet):
    """ViewSet for AssetCategory"""
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    filterset_fields = ['is_active', 'parent']


class LocationViewSet(BaseConfigViewSet):
    """ViewSet for Location"""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filterset_fields = ['is_active', 'city', 'state', 'country']


class PriorityViewSet(BaseConfigViewSet):
    """ViewSet for Priority"""
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    filterset_fields = ['is_active', 'level']
    ordering = ['level']


class WorkOrderTypeViewSet(BaseConfigViewSet):
    """ViewSet for WorkOrderType"""
    queryset = WorkOrderType.objects.all()
    serializer_class = WorkOrderTypeSerializer
    filterset_fields = ['is_active', 'requires_approval']


class SystemParameterViewSet(viewsets.ModelViewSet):
    """ViewSet for SystemParameter"""
    queryset = SystemParameter.objects.all()
    serializer_class = SystemParameterSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['key', 'description']
    ordering_fields = ['key', 'updated_at']
    ordering = ['key']
    
    def perform_update(self, serializer):
        """Log parameter changes"""
        old_instance = self.get_object()
        instance = serializer.save(updated_by=self.request.user)
        
        changes = {
            'key': instance.key,
            'old_value': old_instance.value,
            'new_value': instance.value
        }
        
        AuditLog.log_change(instance, 'UPDATE', self.request.user, changes, self.request)
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Get parameter by key"""
        key = request.query_params.get('key')
        if not key:
            return Response({'error': 'key parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            param = SystemParameter.objects.get(key=key)
            serializer = self.get_serializer(param)
            return Response(serializer.data)
        except SystemParameter.DoesNotExist:
            return Response({'error': 'Parameter not found'}, status=status.HTTP_404_NOT_FOUND)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AuditLog (read-only)"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['model_name', 'action', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def for_object(self, request):
        """Get audit logs for a specific object"""
        model_name = request.query_params.get('model_name')
        object_id = request.query_params.get('object_id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model_name and object_id parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.queryset.filter(model_name=model_name, object_id=object_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
