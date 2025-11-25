"""Views for inventory"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import CanManageInventory
from .models import SparePart, StockMovement
from .serializers import (
    SparePartSerializer,
    StockMovementSerializer,
    StockAdjustmentSerializer
)


class SparePartViewSet(viewsets.ModelViewSet):
    """ViewSet for spare parts"""
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['part_number', 'name', 'description']
    ordering_fields = ['name', 'quantity', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Only ADMIN and SUPERVISOR can create/update/delete"""
        if self.action == 'health':
            return []
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanManageInventory()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """Health check endpoint for debugging"""
        try:
            count = SparePart.objects.count()
            return Response({
                'status': 'ok',
                'spare_parts_count': count,
                'message': f'Found {count} spare parts in database'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock for a spare part"""
        spare_part = self.get_object()
        
        serializer = StockAdjustmentSerializer(data=request.data)
        if serializer.is_valid():
            # Create stock movement
            movement = StockMovement(
                spare_part=spare_part,
                movement_type=serializer.validated_data['movement_type'],
                quantity=serializer.validated_data['quantity'],
                work_order_id=serializer.validated_data.get('work_order'),
                performed_by=request.user,
                notes=serializer.validated_data.get('notes', '')
            )
            
            try:
                movement.save()
                
                # TODO: Create alert if low stock (Task 8)
                if spare_part.is_low_stock():
                    pass  # Create alert
                
                return Response(
                    StockMovementSerializer(movement).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get spare parts with low stock"""
        queryset = self.filter_queryset(self.get_queryset())
        low_stock_parts = [part for part in queryset if part.is_low_stock()]
        
        page = self.paginate_queryset(low_stock_parts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(low_stock_parts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Get stock movements for a spare part"""
        spare_part = self.get_object()
        movements = spare_part.movements.all()
        
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = StockMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for stock movements (read-only)"""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['spare_part', 'movement_type', 'work_order', 'performed_by']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return StockMovement.objects.all().select_related(
            'spare_part', 'work_order', 'performed_by'
        )
