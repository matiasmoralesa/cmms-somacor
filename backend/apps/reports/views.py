"""
Views for reports app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv
import json
from .services import (
    KPICalculationService,
    WorkOrderReportService,
    AssetDowntimeReportService,
    SparePartConsumptionReportService
)
import logging

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for generating reports
    """
    permission_classes = [IsAuthenticated]
    
    def _parse_date_range(self, request):
        """Parse start_date and end_date from request"""
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        return start_date, end_date

    @action(detail=False, methods=['get'])
    def kpis(self, request):
        """Get KPI metrics (MTBF, MTTR, OEE)"""
        start_date, end_date = self._parse_date_range(request)
        asset_id = request.query_params.get('asset_id')
        
        try:
            kpi_service = KPICalculationService()
            
            # Calculate MTBF
            mtbf = kpi_service.calculate_mtbf(asset_id, start_date, end_date)
            
            # Calculate MTTR
            mttr = kpi_service.calculate_mttr(asset_id, start_date, end_date)
            
            # Calculate OEE if asset_id provided
            oee = None
            if asset_id:
                oee = kpi_service.calculate_oee(asset_id, start_date, end_date)
            
            return Response({
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'mtbf': mtbf,
                'mttr': mttr,
                'oee': oee
            })
            
        except Exception as e:
            logger.error(f"Error generating KPI report: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def work_orders_summary(self, request):
        """Get work orders summary report"""
        start_date, end_date = self._parse_date_range(request)
        
        try:
            report_service = WorkOrderReportService()
            summary = report_service.generate_summary_report(start_date, end_date)
            
            return Response({
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': summary
            })
            
        except Exception as e:
            logger.error(f"Error generating work orders summary: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def asset_downtime(self, request):
        """Get asset downtime report"""
        start_date, end_date = self._parse_date_range(request)
        
        try:
            report_service = AssetDowntimeReportService()
            downtime = report_service.generate_downtime_report(start_date, end_date)
            
            return Response({
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'downtime_by_asset': downtime
            })
            
        except Exception as e:
            logger.error(f"Error generating downtime report: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def spare_part_consumption(self, request):
        """Get spare part consumption report"""
        start_date, end_date = self._parse_date_range(request)
        
        try:
            report_service = SparePartConsumptionReportService()
            consumption = report_service.generate_consumption_report(start_date, end_date)
            
            return Response({
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'consumption': consumption
            })
            
        except Exception as e:
            logger.error(f"Error generating consumption report: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export report as CSV"""
        report_type = request.query_params.get('report_type', 'work_orders_summary')
        start_date, end_date = self._parse_date_range(request)
        
        try:
            # Generate report data based on type
            if report_type == 'work_orders_summary':
                service = WorkOrderReportService()
                data = service.generate_summary_report(start_date, end_date)
                filename = 'work_orders_summary.csv'
                
                # Create CSV
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                writer = csv.writer(response)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Work Orders', data['total']])
                writer.writerow(['Avg Completion Hours', data['avg_completion_hours']])
                writer.writerow(['Total Hours', data['total_hours']])
                
                writer.writerow([])
                writer.writerow(['Status', 'Count'])
                for status_key, count in data['by_status'].items():
                    writer.writerow([status_key, count])
                
                return response
                
            elif report_type == 'asset_downtime':
                service = AssetDowntimeReportService()
                data = service.generate_downtime_report(start_date, end_date)
                filename = 'asset_downtime.csv'
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                writer = csv.writer(response)
                writer.writerow(['Asset Name', 'Asset Code', 'Vehicle Type', 'Total Downtime (hrs)', 'Work Order Count', 'Avg Downtime (hrs)'])
                
                for item in data:
                    writer.writerow([
                        item['asset__name'],
                        item['asset__asset_code'],
                        item['asset__vehicle_type'],
                        item['total_downtime_hours'],
                        item['work_order_count'],
                        item['avg_downtime_hours']
                    ])
                
                return response
            
            elif report_type == 'spare_part_consumption':
                service = SparePartConsumptionReportService()
                data = service.generate_consumption_report(start_date, end_date)
                filename = 'spare_part_consumption.csv'
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                writer = csv.writer(response)
                writer.writerow(['Part Name', 'Part Number', 'Total Quantity', 'Movement Count', 'Total Cost'])
                
                for item in data['consumption_by_part']:
                    writer.writerow([
                        item['spare_part__name'],
                        item['spare_part__part_number'],
                        item['total_quantity'],
                        item['movement_count'],
                        item.get('total_cost', 0)
                    ])
                
                return response
            
            else:
                return Response(
                    {'error': 'Invalid report type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get summary data for frontend dashboard"""
        from apps.assets.models import Asset
        from apps.work_orders.models import WorkOrder
        from apps.maintenance.models import MaintenancePlan
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        try:
            # Calculate stats
            active_work_orders = WorkOrder.objects.filter(
                status__in=['PENDING', 'IN_PROGRESS']
            ).count()
            
            operational_assets = Asset.objects.filter(
                status='OPERATIONAL'
            ).count()
            
            # Pending maintenance (plans that are due soon)
            today = datetime.now().date()
            pending_maintenance = MaintenancePlan.objects.filter(
                is_active=True,
                next_maintenance_date__lte=today + timedelta(days=7)
            ).count()
            
            # Critical alerts (high priority pending work orders)
            critical_alerts = WorkOrder.objects.filter(
                status__in=['PENDING', 'IN_PROGRESS'],
                priority='HIGH'
            ).count()
            
            # Calculate changes (simplified - comparing to last month)
            last_month_start = today - timedelta(days=60)
            last_month_end = today - timedelta(days=30)
            
            last_month_wo = WorkOrder.objects.filter(
                created_at__gte=last_month_start,
                created_at__lte=last_month_end,
                status__in=['PENDING', 'IN_PROGRESS']
            ).count()
            
            wo_change = self._calculate_change(active_work_orders, last_month_wo)
            
            # Maintenance trend (last 6 months)
            maintenance_trend = []
            months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            
            for i in range(6):
                month_start = today - timedelta(days=30 * (6 - i))
                month_end = today - timedelta(days=30 * (5 - i))
                
                preventivo = WorkOrder.objects.filter(
                    work_order_type='PREVENTIVE',
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                correctivo = WorkOrder.objects.filter(
                    work_order_type='CORRECTIVE',
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                predictivo = WorkOrder.objects.filter(
                    work_order_type='PREDICTIVE',
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                month_index = (month_start.month - 1) % 12
                maintenance_trend.append({
                    'month': months[month_index],
                    'preventivo': preventivo,
                    'correctivo': correctivo,
                    'predictivo': predictivo
                })
            
            # Work orders by priority
            work_orders_by_priority = []
            for priority, label in [('HIGH', 'Alta'), ('MEDIUM', 'Media'), ('LOW', 'Baja')]:
                count = WorkOrder.objects.filter(
                    status__in=['PENDING', 'IN_PROGRESS'],
                    priority=priority
                ).count()
                work_orders_by_priority.append({
                    'priority': label,
                    'count': count
                })
            
            # Asset health
            asset_health = []
            for status, label, color in [
                ('OPERATIONAL', 'Operativo', '#22c55e'),
                ('MAINTENANCE', 'Mantenimiento', '#f59e0b'),
                ('OUT_OF_SERVICE', 'Fuera de Servicio', '#ef4444')
            ]:
                count = Asset.objects.filter(status=status).count()
                asset_health.append({
                    'name': label,
                    'value': count,
                    'color': color
                })
            
            return Response({
                'stats': {
                    'active_work_orders': active_work_orders,
                    'operational_assets': operational_assets,
                    'pending_maintenance': pending_maintenance,
                    'critical_alerts': critical_alerts,
                    'work_orders_change': wo_change,
                    'assets_change': '+5%',
                    'maintenance_change': '-3%',
                    'alerts_change': '+2%'
                },
                'maintenance_trend': maintenance_trend,
                'work_orders_by_priority': work_orders_by_priority,
                'asset_health': asset_health
            })
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _calculate_change(self, current, previous):
        """Calculate percentage change"""
        if previous == 0:
            return '+100%' if current > 0 else '0%'
        
        change = ((current - previous) / previous) * 100
        sign = '+' if change >= 0 else ''
        return f'{sign}{int(change)}%'
