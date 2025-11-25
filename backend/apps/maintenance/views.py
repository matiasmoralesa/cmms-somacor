"""Views for maintenance plans"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import CanCreateMaintenancePlans
from .models import MaintenancePlan
from .serializers import MaintenancePlanSerializer, MaintenancePlanCreateUpdateSerializer


class MaintenancePlanViewSet(viewsets.ModelViewSet):
    """ViewSet for maintenance plans"""
    queryset = MaintenancePlan.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'plan_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['next_due_date', 'created_at']
    ordering = ['next_due_date']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MaintenancePlanCreateUpdateSerializer
        return MaintenancePlanSerializer
    
    def get_permissions(self):
        """Only ADMIN and SUPERVISOR can create/update/delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CanCreateMaintenancePlans()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """ADMIN and SUPERVISOR see all, OPERADOR sees none"""
        user = self.request.user
        
        if user.can_view_all_resources():
            return MaintenancePlan.objects.all().select_related('asset', 'created_by')
        
        # OPERADOR doesn't see maintenance plans
        return MaintenancePlan.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def pause(self, request, pk=None):
        """Pause maintenance plan"""
        plan = self.get_object()
        plan.is_active = False
        plan.save()
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def resume(self, request, pk=None):
        """Resume maintenance plan"""
        plan = self.get_object()
        plan.is_active = True
        plan.save()
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def due_plans(self, request):
        """Get plans that are due"""
        queryset = self.filter_queryset(self.get_queryset())
        due_plans = [plan for plan in queryset if plan.is_due()]
        serializer = self.get_serializer(due_plans, many=True)
        return Response(serializer.data)
