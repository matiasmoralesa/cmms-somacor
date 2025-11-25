"""Views for assets"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsAdminOrSupervisor, CanViewAllResources
from core.utils import filter_queryset_by_role
from .models import Asset, AssetDocument, Location
from .serializers import (
    AssetSerializer,
    AssetListSerializer,
    AssetDocumentSerializer,
    LocationSerializer,
    AssetStatusUpdateSerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Location management.
    Only ADMIN users can create, update, or delete locations.
    """
    queryset = Location.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'address', 'city', 'region']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        from .serializers import LocationListSerializer
        if self.action == 'list':
            return LocationListSerializer
        return LocationSerializer
    
    def get_permissions(self):
        """
        ADMIN can do everything
        Others can only read
        """
        from core.permissions import IsAdmin
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter locations based on query parameters"""
        queryset = Location.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion if location has associated assets
        """
        instance = self.get_object()
        
        if not instance.can_be_deleted():
            return Response(
                {
                    'error': 'No se puede eliminar esta ubicación porque tiene activos asociados.',
                    'asset_count': instance.assets.count()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def assets(self, request, pk=None):
        """Get all assets in this location"""
        location = self.get_object()
        
        assets = location.assets.all()
        serializer = AssetListSerializer(assets, many=True)
        
        return Response({
            'location': LocationSerializer(location).data,
            'assets': serializer.data,
            'count': assets.count()
        })


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for assets with role-based filtering"""
    queryset = Asset.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['vehicle_type', 'status', 'criticality', 'location']
    search_fields = ['name', 'asset_code', 'serial_number', 'license_plate']
    ordering_fields = ['name', 'asset_code', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        elif self.action == 'update_status':
            return AssetStatusUpdateSerializer
        return AssetSerializer
    
    def get_queryset(self):
        """Filter assets based on user role"""
        user = self.request.user
        queryset = Asset.objects.filter(is_active=True).select_related('location', 'created_by')
        
        # ADMIN and SUPERVISOR see all assets
        if user.can_view_all_resources():
            return queryset
        
        # OPERADOR sees only assigned assets (through work orders)
        from apps.work_orders.models import WorkOrder
        assigned_asset_ids = WorkOrder.objects.filter(
            assigned_to=user
        ).values_list('asset_id', flat=True).distinct()
        
        return queryset.filter(id__in=assigned_asset_ids)
    
    def perform_create(self, serializer):
        """Set created_by on creation"""
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        """Soft delete - set is_active to False"""
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get all documents for an asset"""
        asset = self.get_object()
        documents = asset.documents.all()
        serializer = AssetDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrSupervisor])
    def upload_document(self, request, pk=None):
        """Upload a document for an asset"""
        asset = self.get_object()
        
        serializer = AssetDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(asset=asset, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_vehicle_type(self, request):
        """Get assets grouped by vehicle type"""
        queryset = self.filter_queryset(self.get_queryset())
        
        result = {}
        for choice in Asset.VEHICLE_TYPE_CHOICES:
            vehicle_type = choice[0]
            assets = queryset.filter(vehicle_type=vehicle_type)
            result[vehicle_type] = {
                'name': choice[1],
                'count': assets.count(),
                'assets': AssetSerializer(assets, many=True).data
            }
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get asset statistics"""
        queryset = self.filter_queryset(self.get_queryset())
        
        stats = {
            'total': queryset.count(),
            'by_status': {},
            'by_vehicle_type': {},
            'by_criticality': {},
        }
        
        # By status
        for choice in Asset.STATUS_CHOICES:
            status_code = choice[0]
            count = queryset.filter(status=status_code).count()
            stats['by_status'][status_code] = {
                'name': choice[1],
                'count': count
            }
        
        # By vehicle type
        for choice in Asset.VEHICLE_TYPE_CHOICES:
            vehicle_type = choice[0]
            count = queryset.filter(vehicle_type=vehicle_type).count()
            stats['by_vehicle_type'][vehicle_type] = {
                'name': choice[1],
                'count': count
            }
        
        # By criticality
        for choice in Asset.CRITICALITY_CHOICES:
            criticality = choice[0]
            count = queryset.filter(criticality=criticality).count()
            stats['by_criticality'][criticality] = {
                'name': choice[1],
                'count': count
            }
        
        return Response(stats)
    
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """Update asset status - Available for all authenticated users"""
        asset = self.get_object()
        serializer = AssetStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            old_status = asset.status
            new_status = serializer.validated_data['status']
            notes = serializer.validated_data.get('notes', '')
            
            # Update asset status
            asset.status = new_status
            asset.save()
            
            # Log the status change (optional - could create a StatusHistory model)
            # For now, we'll just return the updated asset
            
            return Response({
                'success': True,
                'message': f'Estado actualizado de {asset.get_status_display(old_status)} a {asset.get_status_display()}',
                'asset': AssetSerializer(asset).data,
                'changed_by': f"{request.user.first_name} {request.user.last_name}",
                'notes': notes
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssetDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for asset documents"""
    queryset = AssetDocument.objects.all()
    serializer_class = AssetDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['asset', 'document_type']
    search_fields = ['file_name', 'description']
    
    def get_queryset(self):
        """Filter documents based on accessible assets"""
        user = self.request.user
        
        # ADMIN and SUPERVISOR see all
        if user.can_view_all_resources():
            return AssetDocument.objects.all()
        
        # OPERADOR sees only documents of assigned assets
        from apps.work_orders.models import WorkOrder
        assigned_asset_ids = WorkOrder.objects.filter(
            assigned_to=user
        ).values_list('asset_id', flat=True).distinct()
        
        return AssetDocument.objects.filter(asset_id__in=assigned_asset_ids)
    
    def perform_create(self, serializer):
        """Set uploaded_by on creation"""
        serializer.save(uploaded_by=self.request.user)

