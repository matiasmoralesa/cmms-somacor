from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.http import HttpResponse
from datetime import datetime, timedelta
from io import BytesIO

from core.permissions import IsAdminOrSupervisor
from .models import AssetStatus, AssetStatusHistory
from .serializers import (
    AssetStatusSerializer,
    AssetStatusCreateSerializer,
    AssetStatusListSerializer,
    AssetStatusHistorySerializer
)
from apps.assets.models import Asset


class AssetStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Asset Status management.
    OPERADOR can create status for assigned assets.
    ADMIN/SUPERVISOR can create status for any asset.
    """
    queryset = AssetStatus.objects.all().select_related('asset', 'reported_by', 'location')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset', 'status_type', 'reported_by']
    search_fields = ['asset__name', 'asset__asset_code', 'condition_notes']
    ordering_fields = ['reported_at', 'odometer_reading']
    ordering = ['-reported_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AssetStatusCreateSerializer
        elif self.action == 'list':
            return AssetStatusListSerializer
        return AssetStatusSerializer
    
    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        queryset = AssetStatus.objects.all().select_related('asset', 'reported_by', 'location')
        
        # OPERADOR only sees their own status updates
        if user.is_operador():
            queryset = queryset.filter(reported_by=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set reported_by to current user"""
        serializer.save(reported_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_assets(self, request):
        """Get assets assigned to current user (OPERADOR)"""
        user = request.user
        
        if not user.is_operador():
            return Response(
                {'error': 'Este endpoint es solo para operadores'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get assets from active work orders
        from apps.work_orders.models import WorkOrder
        assigned_assets = Asset.objects.filter(
            work_orders__assigned_to=user,
            work_orders__status__in=['ASSIGNED', 'IN_PROGRESS'],
            is_active=True
        ).distinct()
        
        from apps.assets.serializers import AssetListSerializer
        serializer = AssetListSerializer(assigned_assets, many=True)
        
        return Response({
            'assets': serializer.data,
            'count': assigned_assets.count()
        })
    
    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>[^/.]+)/history')
    def asset_history(self, request, asset_id=None):
        """Get status history for a specific asset"""
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Activo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get history
        history = AssetStatusHistory.objects.filter(asset=asset).select_related('changed_by')
        serializer = AssetStatusHistorySerializer(history, many=True)
        
        return Response({
            'asset': {
                'id': str(asset.id),
                'name': asset.name,
                'asset_code': asset.asset_code
            },
            'history': serializer.data,
            'count': history.count()
        })
    
    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>[^/.]+)/current')
    def asset_current_status(self, request, asset_id=None):
        """Get current status for a specific asset"""
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Activo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get latest status
        latest_status = AssetStatus.objects.filter(asset=asset).first()
        
        if not latest_status:
            return Response({
                'asset': {
                    'id': str(asset.id),
                    'name': asset.name,
                    'asset_code': asset.asset_code
                },
                'status': None,
                'message': 'No hay registros de estado para este activo'
            })
        
        serializer = AssetStatusSerializer(latest_status)
        return Response({
            'asset': {
                'id': str(asset.id),
                'name': asset.name,
                'asset_code': asset.asset_code
            },
            'status': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>[^/.]+)/chart-data')
    def asset_chart_data(self, request, asset_id=None):
        """Get chart data for asset status history"""
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Activo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get date range from query params (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Get status updates in date range
        status_updates = AssetStatus.objects.filter(
            asset=asset,
            reported_at__gte=start_date
        ).order_by('reported_at')
        
        # Prepare chart data
        chart_data = {
            'labels': [],
            'odometer': [],
            'fuel_level': [],
            'status_timeline': []
        }
        
        for update in status_updates:
            chart_data['labels'].append(update.reported_at.strftime('%Y-%m-%d %H:%M'))
            chart_data['odometer'].append(float(update.odometer_reading) if update.odometer_reading else None)
            chart_data['fuel_level'].append(update.fuel_level)
            chart_data['status_timeline'].append({
                'date': update.reported_at.isoformat(),
                'status': update.status_type,
                'status_display': update.get_status_type_display()
            })
        
        # Get status distribution
        status_distribution = AssetStatus.objects.filter(
            asset=asset,
            reported_at__gte=start_date
        ).values('status_type').annotate(count=Count('id'))
        
        return Response({
            'asset': {
                'id': str(asset.id),
                'name': asset.name,
                'asset_code': asset.asset_code
            },
            'chart_data': chart_data,
            'status_distribution': list(status_distribution),
            'date_range': {
                'start': start_date.isoformat(),
                'end': datetime.now().isoformat(),
                'days': days
            }
        })
    
    @action(detail=False, methods=['get'], url_path='asset/(?P<asset_id>[^/.]+)/maintenance-report')
    def maintenance_report(self, request, asset_id=None):
        """Generate PDF report with all maintenance history"""
        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Activo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all work orders for this asset
        from apps.work_orders.models import WorkOrder
        work_orders = WorkOrder.objects.filter(asset=asset).select_related('assigned_to', 'created_by').order_by('-created_at')
        
        # Get status history
        status_history = AssetStatusHistory.objects.filter(asset=asset).select_related('changed_by').order_by('-changed_at')
        
        # Generate PDF
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
        )
        elements.append(Paragraph(f'Informe de Mantenimiento', title_style))
        elements.append(Paragraph(f'Activo: {asset.name} ({asset.asset_code})', styles['Heading2']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Asset Info
        asset_info = [
            ['Información del Activo', ''],
            ['Nombre:', asset.name],
            ['Código:', asset.asset_code],
            ['Tipo:', asset.get_vehicle_type_display()],
            ['Número de Serie:', asset.serial_number or 'N/A'],
            ['Placa:', asset.license_plate or 'N/A'],
            ['Estado Actual:', asset.get_status_display()],
        ]
        
        asset_table = Table(asset_info, colWidths=[2*inch, 4*inch])
        asset_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(asset_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Work Orders Section
        elements.append(Paragraph('Historial de Órdenes de Trabajo', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        if work_orders.exists():
            wo_data = [['Fecha', 'Título', 'Tipo', 'Estado', 'Asignado a']]
            for wo in work_orders[:20]:  # Limit to last 20
                wo_data.append([
                    wo.created_at.strftime('%Y-%m-%d'),
                    wo.title[:30],
                    wo.get_work_order_type_display(),
                    wo.get_status_display(),
                    wo.assigned_to.get_full_name() if wo.assigned_to else 'N/A'
                ])
            
            wo_table = Table(wo_data, colWidths=[1*inch, 2*inch, 1.2*inch, 1*inch, 1.3*inch])
            wo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(wo_table)
        else:
            elements.append(Paragraph('No hay órdenes de trabajo registradas.', styles['Normal']))
        
        elements.append(PageBreak())
        
        # Status History Section
        elements.append(Paragraph('Historial de Estados', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        if status_history.exists():
            status_data = [['Fecha', 'Estado Anterior', 'Nuevo Estado', 'Odómetro', 'Reportado por']]
            for sh in status_history[:30]:  # Limit to last 30
                status_data.append([
                    sh.changed_at.strftime('%Y-%m-%d %H:%M'),
                    sh.previous_status or 'N/A',
                    sh.new_status,
                    f"{sh.new_odometer}" if sh.new_odometer else 'N/A',
                    sh.changed_by.get_full_name()
                ])
            
            status_table = Table(status_data, colWidths=[1.2*inch, 1.3*inch, 1.3*inch, 1*inch, 1.7*inch])
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(status_table)
        else:
            elements.append(Paragraph('No hay historial de estados registrado.', styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f'Informe generado el {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Return PDF response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="mantenimiento_{asset.asset_code}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
