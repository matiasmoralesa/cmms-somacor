"""
Views for core app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Webhook, WebhookDelivery
from .serializers import (
    WebhookSerializer,
    WebhookDeliverySerializer,
    WebhookTestSerializer
)
from .webhook_service import WebhookService
import logging

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=['Webhooks'],
        summary='Listar webhooks',
        description='Obtiene la lista de webhooks configurados'
    ),
    create=extend_schema(
        tags=['Webhooks'],
        summary='Crear webhook',
        description='Crea un nuevo webhook para recibir notificaciones de eventos'
    ),
    retrieve=extend_schema(
        tags=['Webhooks'],
        summary='Obtener webhook',
        description='Obtiene los detalles de un webhook específico'
    ),
    update=extend_schema(
        tags=['Webhooks'],
        summary='Actualizar webhook',
        description='Actualiza la configuración de un webhook'
    ),
    partial_update=extend_schema(
        tags=['Webhooks'],
        summary='Actualizar parcialmente webhook',
        description='Actualiza parcialmente la configuración de un webhook'
    ),
    destroy=extend_schema(
        tags=['Webhooks'],
        summary='Eliminar webhook',
        description='Elimina un webhook'
    )
)
class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for managing webhooks"""
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'url']
    filterset_fields = ['is_active']
    ordering_fields = ['created_at', 'last_delivery_at', 'total_deliveries']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter webhooks by user"""
        if self.request.user.is_superuser:
            return Webhook.objects.all()
        return Webhook.objects.filter(created_by=self.request.user)
    
    @extend_schema(
        tags=['Webhooks'],
        summary='Probar webhook',
        description='Envía un evento de prueba al webhook',
        request=WebhookTestSerializer,
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test webhook by sending a test event"""
        webhook = self.get_object()
        serializer = WebhookTestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        event_type = serializer.validated_data['event_type']
        test_payload = serializer.validated_data.get('test_payload', {
            'test': True,
            'message': 'Este es un evento de prueba'
        })
        
        # Deliver test webhook
        delivery = WebhookService.deliver_webhook(webhook, event_type, test_payload)
        
        return Response(
            WebhookDeliverySerializer(delivery).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Webhooks'],
        summary='Regenerar secret',
        description='Regenera el secret del webhook para firmar payloads',
        responses={200: WebhookSerializer}
    )
    @action(detail=True, methods=['post'])
    def regenerate_secret(self, request, pk=None):
        """Regenerate webhook secret"""
        webhook = self.get_object()
        
        import secrets
        webhook.secret = secrets.token_hex(32)
        webhook.save()
        
        return Response(
            WebhookSerializer(webhook).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        tags=['Webhooks'],
        summary='Obtener entregas del webhook',
        description='Obtiene el historial de entregas de un webhook',
        responses={200: WebhookDeliverySerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """Get webhook delivery history"""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all()[:50]  # Last 50 deliveries
        
        return Response(
            WebhookDeliverySerializer(deliveries, many=True).data,
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    list=extend_schema(
        tags=['Webhooks'],
        summary='Listar entregas de webhooks',
        description='Obtiene el historial de entregas de webhooks'
    ),
    retrieve=extend_schema(
        tags=['Webhooks'],
        summary='Obtener entrega de webhook',
        description='Obtiene los detalles de una entrega específica'
    )
)
class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing webhook deliveries (read-only)"""
    queryset = WebhookDelivery.objects.all()
    serializer_class = WebhookDeliverySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['webhook', 'event_type', 'status']
    ordering_fields = ['created_at', 'delivered_at', 'duration_ms']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter deliveries by user's webhooks"""
        if self.request.user.is_superuser:
            return WebhookDelivery.objects.all()
        return WebhookDelivery.objects.filter(webhook__created_by=self.request.user)
    
    @extend_schema(
        tags=['Webhooks'],
        summary='Reintentar entrega',
        description='Reintenta la entrega de un webhook fallido',
        responses={200: WebhookDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed delivery"""
        delivery = self.get_object()
        
        if delivery.status == 'success':
            return Response(
                {'error': 'No se puede reintentar una entrega exitosa'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Deliver webhook again
        new_delivery = WebhookService.deliver_webhook(
            delivery.webhook,
            delivery.event_type,
            delivery.payload
        )
        
        return Response(
            WebhookDeliverySerializer(new_delivery).data,
            status=status.HTTP_200_OK
        )



class ComposerViewSet(viewsets.ViewSet):
    """ViewSet for Cloud Composer DAG management"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(
        tags=['Cloud Composer'],
        summary='Listar DAGs',
        description='Obtiene la lista de DAGs disponibles en Cloud Composer'
    )
    @action(detail=False, methods=['get'])
    def list_dags(self, request):
        """List available DAGs"""
        # Placeholder - implement actual Cloud Composer integration
        return Response({
            'dags': [
                {
                    'dag_id': 'etl_ml_training',
                    'is_paused': False,
                    'description': 'ETL y entrenamiento de modelo ML'
                },
                {
                    'dag_id': 'preventive_maintenance',
                    'is_paused': False,
                    'description': 'Generación de órdenes de mantenimiento preventivo'
                },
                {
                    'dag_id': 'report_generation',
                    'is_paused': False,
                    'description': 'Generación de reportes semanales'
                }
            ]
        })
    
    @extend_schema(
        tags=['Cloud Composer'],
        summary='Trigger ETL y ML Training',
        description='Inicia el DAG de ETL y entrenamiento de modelo ML'
    )
    @action(detail=False, methods=['post'])
    def trigger_etl_ml_training(self, request):
        """Trigger ETL and ML training DAG"""
        # Placeholder - implement actual Cloud Composer integration
        return Response({
            'message': 'DAG triggered successfully',
            'dag_id': 'etl_ml_training',
            'dag_run_id': 'manual__2024-11-13T00:00:00+00:00'
        })
    
    @extend_schema(
        tags=['Cloud Composer'],
        summary='Trigger Preventive Maintenance',
        description='Inicia el DAG de generación de mantenimiento preventivo'
    )
    @action(detail=False, methods=['post'])
    def trigger_preventive_maintenance(self, request):
        """Trigger preventive maintenance DAG"""
        # Placeholder - implement actual Cloud Composer integration
        return Response({
            'message': 'DAG triggered successfully',
            'dag_id': 'preventive_maintenance',
            'dag_run_id': 'manual__2024-11-13T00:00:00+00:00'
        })
    
    @extend_schema(
        tags=['Cloud Composer'],
        summary='Trigger Report Generation',
        description='Inicia el DAG de generación de reportes'
    )
    @action(detail=False, methods=['post'])
    def trigger_report_generation(self, request):
        """Trigger report generation DAG"""
        # Placeholder - implement actual Cloud Composer integration
        return Response({
            'message': 'DAG triggered successfully',
            'dag_id': 'report_generation',
            'dag_run_id': 'manual__2024-11-13T00:00:00+00:00'
        })



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .health_checks import HealthChecker


@extend_schema(
    tags=['Health'],
    summary='Liveness probe',
    description='Endpoint simple para verificar que el servicio está vivo (para Kubernetes/Cloud Run)',
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_probe(request):
    """
    Liveness probe - checks if service is alive
    Used by Kubernetes/Cloud Run to determine if container should be restarted
    """
    return Response({
        'status': 'alive',
        'timestamp': time.time()
    })


@extend_schema(
    tags=['Health'],
    summary='Readiness probe',
    description='Verifica que el servicio está listo para recibir tráfico (DB y dependencias funcionando)',
    responses={
        200: {'type': 'object', 'properties': {'status': {'type': 'string'}}},
        503: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'error': {'type': 'string'}}}
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_probe(request):
    """
    Readiness probe - checks if service is ready to receive traffic
    Used by Kubernetes/Cloud Run to determine if container should receive requests
    """
    # Check critical dependencies
    db_check = HealthChecker.check_database()
    
    if db_check['status'] == 'healthy':
        return Response({
            'status': 'ready',
            'timestamp': time.time()
        })
    else:
        return Response({
            'status': 'not_ready',
            'error': db_check.get('error', 'Database unhealthy'),
            'timestamp': time.time()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@extend_schema(
    tags=['Health'],
    summary='Health check completo',
    description='Verifica el estado de salud de todos los componentes del sistema',
    responses={
        200: {'type': 'object'},
        503: {'type': 'object'}
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Full health check - checks all system dependencies
    """
    health_status = HealthChecker.perform_full_health_check()
    
    if health_status['status'] == 'unhealthy':
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        return Response(health_status)


import time


# Temporary endpoint for running migrations
from django.core.management import call_command
from io import StringIO


@extend_schema(
    tags=['Admin'],
    summary='Crear migraciones (TEMPORAL)',
    description='Endpoint temporal para crear migraciones. ELIMINAR después de usar.',
    responses={
        200: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'output': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        500: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def make_migrations(request):
    """
    Crea las migraciones de base de datos
    NOTA: Este endpoint es TEMPORAL y debe ser eliminado después de usar
    """
    try:
        # Capturar output
        output = StringIO()
        call_command('makemigrations', verbosity=2, stdout=output)
        
        return Response({
            'status': 'success',
            'message': 'Migraciones creadas correctamente',
            'output': output.getvalue()
        })
    except Exception as e:
        logger.error(f"Error creando migraciones: {e}")
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Admin'],
    summary='Ejecutar migraciones (TEMPORAL)',
    description='Endpoint temporal para ejecutar migraciones de base de datos. ELIMINAR después de usar.',
    responses={
        200: {'type': 'object', 'properties': {'status': {'type': 'string'}, 'output': {'type': 'string'}}},
        403: {'type': 'object', 'properties': {'error': {'type': 'string'}}},
        500: {'type': 'object', 'properties': {'error': {'type': 'string'}}}
    }
)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def run_migrations(request):
    """
    Ejecuta las migraciones de base de datos
    NOTA: Este endpoint es TEMPORAL y debe ser eliminado después de usar
    """
    try:
        # Capturar output de las migraciones
        output = StringIO()
        call_command('migrate', verbosity=2, stdout=output)
        
        return Response({
            'status': 'success',
            'message': 'Migraciones ejecutadas correctamente',
            'output': output.getvalue()
        })
    except Exception as e:
        logger.error(f"Error ejecutando migraciones: {e}")
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Dashboard Views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.maintenance.models import MaintenancePlan


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Obtiene estadísticas principales del dashboard"""
    active_work_orders = WorkOrder.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).count()
    operational_assets = Asset.objects.filter(status='OPERATIONAL').count()
    pending_maintenance = MaintenancePlan.objects.filter(
        is_active=True,
        next_due_date__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    critical_alerts = WorkOrder.objects.filter(
        priority='URGENT',
        status__in=['PENDING', 'IN_PROGRESS']
    ).count()
    
    last_month = timezone.now() - timedelta(days=30)
    active_work_orders_last_month = WorkOrder.objects.filter(
        status__in=['PENDING', 'IN_PROGRESS'],
        created_at__lte=last_month
    ).count()
    operational_assets_last_month = Asset.objects.filter(
        status='OPERATIONAL',
        created_at__lte=last_month
    ).count()
    
    def calculate_change(current, previous):
        if previous == 0:
            return "+100%" if current > 0 else "0%"
        change = ((current - previous) / previous) * 100
        return f"{'+' if change > 0 else ''}{change:.1f}%"
    
    return Response({
        'active_work_orders': active_work_orders,
        'operational_assets': operational_assets,
        'pending_maintenance': pending_maintenance,
        'critical_alerts': critical_alerts,
        'work_orders_change': calculate_change(active_work_orders, active_work_orders_last_month),
        'assets_change': calculate_change(operational_assets, operational_assets_last_month),
        'maintenance_change': f"-{pending_maintenance}",
        'alerts_change': f"+{critical_alerts}",
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def maintenance_trend(request):
    """Obtiene tendencia de mantenimientos por mes"""
    months = []
    current_date = timezone.now()
    
    for i in range(5, -1, -1):
        month_date = current_date - timedelta(days=30 * i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        preventivo = MaintenancePlan.objects.filter(
            plan_type='PREVENTIVE',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        # No hay tipo CORRECTIVE en MaintenancePlan, solo en WorkOrder
        correctivo = 0
        predictivo = MaintenancePlan.objects.filter(
            plan_type='PREDICTIVE',
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        months.append({
            'month': month_date.strftime('%b'),
            'preventivo': preventivo,
            'correctivo': correctivo,
            'predictivo': predictivo,
        })
    
    return Response(months)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def work_orders_by_priority(request):
    """Obtiene distribución de órdenes de trabajo por prioridad"""
    priorities = WorkOrder.objects.filter(
        status__in=['PENDING', 'IN_PROGRESS']
    ).values('priority').annotate(count=Count('id'))
    
    priority_map = {'LOW': 'Baja', 'MEDIUM': 'Media', 'HIGH': 'Alta', 'URGENT': 'Urgente'}
    data = [{'priority': priority_map.get(p['priority'], p['priority']), 'count': p['count']} for p in priorities]
    
    existing_priorities = [item['priority'] for item in data]
    for key, value in priority_map.items():
        if value not in existing_priorities:
            data.append({'priority': value, 'count': 0})
    
    priority_order = ['Baja', 'Media', 'Alta', 'Urgente']
    data.sort(key=lambda x: priority_order.index(x['priority']) if x['priority'] in priority_order else 999)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def asset_health(request):
    """Obtiene estado de salud de activos"""
    operational = Asset.objects.filter(status='OPERATIONAL').count()
    maintenance = Asset.objects.filter(status='MAINTENANCE').count()
    out_of_service = Asset.objects.filter(status='OUT_OF_SERVICE').count()
    
    return Response([
        {'name': 'Operativo', 'value': operational, 'color': '#22c55e'},
        {'name': 'Mantenimiento', 'value': maintenance, 'color': '#f59e0b'},
        {'name': 'Fuera de Servicio', 'value': out_of_service, 'color': '#ef4444'}
    ])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Obtiene todos los datos del dashboard en una sola llamada"""
    return Response({
        'stats': dashboard_stats(request).data,
        'maintenance_trend': maintenance_trend(request).data,
        'work_orders_by_priority': work_orders_by_priority(request).data,
        'asset_health': asset_health(request).data,
    })
