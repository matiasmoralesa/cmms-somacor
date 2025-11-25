"""
Views for predictions app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import models
from .models import FailurePrediction, Alert
from .serializers import (
    FailurePredictionSerializer,
    AlertSerializer,
    AlertActionSerializer
)


class FailurePredictionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FailurePrediction model
    """
    queryset = FailurePrediction.objects.select_related('asset').all()
    serializer_class = FailurePredictionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['asset', 'risk_level']
    search_fields = ['asset__name', 'asset__asset_code']
    ordering_fields = ['prediction_date', 'failure_probability', 'risk_level']
    ordering = ['-prediction_date']

    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get high risk predictions (probability >= 50%)"""
        predictions = self.queryset.filter(failure_probability__gte=50)
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def asset_health_score(self, request, pk=None):
        """Calculate asset health score based on predictions"""
        prediction = self.get_object()
        
        # Simple health score calculation (100 - failure_probability)
        health_score = 100 - float(prediction.failure_probability)
        
        return Response({
            'asset_id': str(prediction.asset.id),
            'asset_name': prediction.asset.name,
            'health_score': health_score,
            'failure_probability': float(prediction.failure_probability),
            'risk_level': prediction.risk_level,
            'last_prediction_date': prediction.prediction_date,
        })
    
    @action(detail=False, methods=['post'])
    def predict_asset(self, request):
        """Generate a new prediction for a specific asset"""
        from apps.assets.models import Asset
        from .ml_service import MLPredictionService
        
        asset_id = request.data.get('asset_id')
        use_vertex_ai = request.data.get('use_vertex_ai', False)
        
        if not asset_id:
            return Response(
                {'error': 'asset_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate prediction
        ml_service = MLPredictionService()
        prediction = ml_service.create_prediction_for_asset(asset)
        
        serializer = self.get_serializer(prediction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def predict_all_assets(self, request):
        """Generate predictions for all operational assets"""
        from apps.assets.models import Asset
        from .ml_service import MLPredictionService
        
        # Get operational assets
        assets = Asset.objects.filter(status__in=['OPERATIONAL', 'MAINTENANCE'])
        
        ml_service = MLPredictionService()
        
        # Load or train model
        if not ml_service.load_model():
            ml_service.train_model()
        
        predictions = []
        for asset in assets:
            try:
                prediction = ml_service.create_prediction_for_asset(asset)
                predictions.append(prediction)
            except Exception as e:
                continue
        
        serializer = self.get_serializer(predictions, many=True)
        return Response({
            'count': len(predictions),
            'predictions': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def asset_health_dashboard(self, request):
        """Get health dashboard data for all assets"""
        from apps.assets.models import Asset
        from django.db.models import Avg, Count
        
        # Get latest prediction for each asset
        assets = Asset.objects.filter(status__in=['OPERATIONAL', 'MAINTENANCE'])
        
        dashboard_data = []
        for asset in assets:
            latest_prediction = self.queryset.filter(asset=asset).first()
            
            if latest_prediction:
                health_score = 100 - float(latest_prediction.failure_probability)
                dashboard_data.append({
                    'asset_id': str(asset.id),
                    'asset_name': asset.name,
                    'asset_code': asset.asset_code,
                    'vehicle_type': asset.vehicle_type,
                    'health_score': round(health_score, 2),
                    'failure_probability': float(latest_prediction.failure_probability),
                    'risk_level': latest_prediction.risk_level,
                    'risk_level_display': latest_prediction.get_risk_level_display(),
                    'last_prediction': latest_prediction.prediction_date,
                    'predicted_failure_date': latest_prediction.predicted_failure_date,
                })
        
        # Calculate summary statistics
        if dashboard_data:
            avg_health = sum(d['health_score'] for d in dashboard_data) / len(dashboard_data)
            critical_count = sum(1 for d in dashboard_data if d['risk_level'] == 'CRITICAL')
            high_count = sum(1 for d in dashboard_data if d['risk_level'] == 'HIGH')
            medium_count = sum(1 for d in dashboard_data if d['risk_level'] == 'MEDIUM')
            low_count = sum(1 for d in dashboard_data if d['risk_level'] == 'LOW')
        else:
            avg_health = 100
            critical_count = high_count = medium_count = low_count = 0
        
        return Response({
            'summary': {
                'total_assets': len(dashboard_data),
                'average_health_score': round(avg_health, 2),
                'critical_risk': critical_count,
                'high_risk': high_count,
                'medium_risk': medium_count,
                'low_risk': low_count,
            },
            'assets': dashboard_data
        })
    
    @action(detail=False, methods=['get'])
    def prediction_trends(self, request):
        """Get prediction trends over time"""
        from django.db.models import Avg, Count
        from django.db.models.functions import TruncDate
        from datetime import timedelta
        from django.utils import timezone
        
        # Get predictions from last 30 days
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        trends = self.queryset.filter(
            prediction_date__gte=start_date
        ).annotate(
            date=TruncDate('prediction_date')
        ).values('date').annotate(
            avg_probability=Avg('failure_probability'),
            count=Count('id'),
            critical_count=Count('id', filter=models.Q(risk_level='CRITICAL')),
            high_count=Count('id', filter=models.Q(risk_level='HIGH')),
        ).order_by('date')
        
        return Response(list(trends))


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Alert model
    """
    queryset = Alert.objects.select_related(
        'asset', 'work_order', 'prediction', 'resolved_by'
    ).all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'is_read', 'is_resolved']
    search_fields = ['title', 'message', 'asset__name']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread alerts"""
        alerts = self.queryset.filter(is_read=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get critical unresolved alerts"""
        alerts = self.queryset.filter(
            severity='CRITICAL',
            is_resolved=False
        )
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.mark_as_read()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve alert"""
        alert = self.get_object()
        alert.resolve(request.user)
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get alert statistics"""
        total = self.queryset.count()
        unread = self.queryset.filter(is_read=False).count()
        unresolved = self.queryset.filter(is_resolved=False).count()
        critical = self.queryset.filter(
            severity='CRITICAL',
            is_resolved=False
        ).count()

        return Response({
            'total': total,
            'unread': unread,
            'unresolved': unresolved,
            'critical': critical,
        })
