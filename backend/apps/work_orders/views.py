"""Views for work orders"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from core.permissions import CanCreateWorkOrders
from .models import WorkOrder
from .serializers import (
    WorkOrderSerializer,
    WorkOrderCreateSerializer,
    WorkOrderUpdateSerializer,
    WorkOrderCompleteSerializer,
    WorkOrderStatusChangeSerializer
)


class WorkOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for work orders with role-based filtering"""
    queryset = WorkOrder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'work_order_type', 'assigned_to', 'asset']
    search_fields = ['work_order_number', 'title', 'description']
    ordering_fields = ['created_at', 'scheduled_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WorkOrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkOrderUpdateSerializer
        elif self.action == 'complete':
            return WorkOrderCompleteSerializer
        elif self.action == 'change_status':
            return WorkOrderStatusChangeSerializer
        return WorkOrderSerializer
    
    def get_permissions(self):
        """Only ADMIN and SUPERVISOR can create/delete"""
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), CanCreateWorkOrders()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter work orders based on user role"""
        user = self.request.user
        queryset = WorkOrder.objects.all().select_related(
            'asset', 'assigned_to', 'created_by'
        )
        
        # Filter by asset status (has_asset parameter)
        has_asset = self.request.query_params.get('has_asset')
        if has_asset is not None:
            if has_asset.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(asset__isnull=False)
            elif has_asset.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(asset__isnull=True)
        
        # ADMIN and SUPERVISOR see all
        if user.can_view_all_resources():
            return queryset
        
        # OPERADOR sees only assigned work orders
        return queryset.filter(assigned_to=user)
    
    def perform_create(self, serializer):
        """Set created_by and initial status"""
        import logging
        logger = logging.getLogger(__name__)
        
        work_order = serializer.save(created_by=self.request.user)
        
        # Log if creating without asset
        if not work_order.asset:
            logger.info(
                f"Creating work order without asset. "
                f"User: {self.request.user.email}, "
                f"Type: {work_order.work_order_type}, "
                f"WO Number: {work_order.work_order_number}"
            )
        
        # If assigned, change status to ASSIGNED
        if work_order.assigned_to:
            work_order.status = WorkOrder.STATUS_ASSIGNED
            work_order.save()
        
        # TODO: Send notification via Pub/Sub (Task 10)
    
    def perform_update(self, serializer):
        """Handle status changes on update"""
        instance = self.get_object()
        old_assigned_to = instance.assigned_to
        
        work_order = serializer.save()
        
        # If assigned_to changed, update status
        if work_order.assigned_to and work_order.assigned_to != old_assigned_to:
            if work_order.status == WorkOrder.STATUS_PENDING:
                work_order.status = WorkOrder.STATUS_ASSIGNED
                work_order.save()
        
        # TODO: Send notification via Pub/Sub (Task 10)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a work order"""
        work_order = self.get_object()
        
        # Check if user can complete (assigned user or ADMIN/SUPERVISOR)
        if not request.user.can_view_all_resources():
            if work_order.assigned_to != request.user:
                return Response(
                    {'error': 'Solo puedes completar OTs asignadas a ti'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            work_order.status = WorkOrder.STATUS_COMPLETED
            work_order.actual_hours = serializer.validated_data['actual_hours']
            work_order.completion_notes = serializer.validated_data['completion_notes']
            work_order.completed_at = timezone.now()
            work_order.save()
            
            # TODO: Send notification via Pub/Sub (Task 10)
            
            return Response(
                WorkOrderSerializer(work_order).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Change work order status"""
        work_order = self.get_object()
        
        serializer = self.get_serializer(
            data=request.data,
            context={'instance': work_order}
        )
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            
            # Set timestamps based on status
            if new_status == WorkOrder.STATUS_IN_PROGRESS and not work_order.started_at:
                work_order.started_at = timezone.now()
            
            work_order.status = new_status
            work_order.save()
            
            # TODO: Send notification via Pub/Sub (Task 10)
            
            return Response(
                WorkOrderSerializer(work_order).data,
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get work orders assigned to current user"""
        queryset = self.filter_queryset(
            self.get_queryset().filter(assigned_to=request.user)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def without_asset(self, request):
        """Get all work orders without asset assigned"""
        queryset = self.filter_queryset(
            self.get_queryset().filter(asset__isnull=True)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get work order statistics including asset assignment"""
        queryset = self.filter_queryset(self.get_queryset())
        
        total = queryset.count()
        with_asset = queryset.filter(asset__isnull=False).count()
        without_asset = queryset.filter(asset__isnull=True).count()
        
        stats = {
            'total': total,
            'with_asset': with_asset,
            'without_asset': without_asset,
            'percentage_without_asset': round((without_asset / total * 100), 2) if total > 0 else 0,
            'by_status': {},
            'by_priority': {},
            'by_type': {},
        }
        
        # By status
        for choice in WorkOrder.STATUS_CHOICES:
            status_code = choice[0]
            count = queryset.filter(status=status_code).count()
            stats['by_status'][status_code] = {
                'name': choice[1],
                'count': count
            }
        
        # By priority
        for choice in WorkOrder.PRIORITY_CHOICES:
            priority = choice[0]
            count = queryset.filter(priority=priority).count()
            stats['by_priority'][priority] = {
                'name': choice[1],
                'count': count
            }
        
        # By type
        for choice in WorkOrder.TYPE_CHOICES:
            wo_type = choice[0]
            count = queryset.filter(work_order_type=wo_type).count()
            stats['by_type'][wo_type] = {
                'name': choice[1],
                'count': count
            }
        
        return Response(stats)
