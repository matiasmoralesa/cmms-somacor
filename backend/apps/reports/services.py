"""
Report Generation Services
"""
from django.db.models import Count, Avg, Sum, F, Q, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta, datetime
from apps.work_orders.models import WorkOrder
from apps.assets.models import Asset
from apps.inventory.models import SparePart, StockMovement
from apps.maintenance.models import MaintenancePlan
import logging

logger = logging.getLogger(__name__)


class KPICalculationService:
    """Service for calculating KPIs"""
    
    @staticmethod
    def calculate_mtbf(asset_id=None, start_date=None, end_date=None):
        """
        Calculate Mean Time Between Failures (MTBF)
        MTBF = Total Operating Time / Number of Failures
        """
        filters = Q(work_order_type='CORRECTIVE', status='COMPLETED')
        
        if asset_id:
            filters &= Q(asset_id=asset_id)
        if start_date:
            filters &= Q(completed_at__gte=start_date)
        if end_date:
            filters &= Q(completed_at__lte=end_date)
        
        failures = WorkOrder.objects.filter(filters).order_by('asset', 'completed_at')
        
        mtbf_by_asset = {}
        
        for asset in Asset.objects.filter(status='ACTIVE'):
            asset_failures = failures.filter(asset=asset)
            
            if asset_failures.count() < 2:
                continue
            
            # Calculate time between failures
            times_between = []
            prev_failure = None
            
            for failure in asset_failures:
                if prev_failure:
                    time_diff = (failure.completed_at - prev_failure.completed_at).total_seconds() / 3600  # hours
                    times_between.append(time_diff)
                prev_failure = failure
            
            if times_between:
                mtbf_by_asset[str(asset.id)] = {
                    'asset_name': asset.name,
                    'asset_code': asset.asset_code,
                    'mtbf_hours': sum(times_between) / len(times_between),
                    'failure_count': asset_failures.count()
                }
        
        return mtbf_by_asset

    @staticmethod
    def calculate_mttr(asset_id=None, start_date=None, end_date=None):
        """
        Calculate Mean Time To Repair (MTTR)
        MTTR = Total Repair Time / Number of Repairs
        """
        filters = Q(status='COMPLETED', actual_hours__isnull=False)
        
        if asset_id:
            filters &= Q(asset_id=asset_id)
        if start_date:
            filters &= Q(completed_at__gte=start_date)
        if end_date:
            filters &= Q(completed_at__lte=end_date)
        
        work_orders = WorkOrder.objects.filter(filters)
        
        mttr_data = work_orders.aggregate(
            avg_repair_hours=Avg('actual_hours'),
            total_repairs=Count('id'),
            total_hours=Sum('actual_hours')
        )
        
        # MTTR by asset
        mttr_by_asset = work_orders.values(
            'asset__id', 'asset__name', 'asset__asset_code'
        ).annotate(
            avg_repair_hours=Avg('actual_hours'),
            repair_count=Count('id')
        )
        
        return {
            'overall': mttr_data,
            'by_asset': list(mttr_by_asset)
        }
    
    @staticmethod
    def calculate_oee(asset_id, start_date, end_date):
        """
        Calculate Overall Equipment Effectiveness (OEE)
        OEE = Availability × Performance × Quality
        
        Simplified version:
        Availability = (Total Time - Downtime) / Total Time
        """
        total_hours = (end_date - start_date).total_seconds() / 3600
        
        # Calculate downtime from work orders
        downtime_wo = WorkOrder.objects.filter(
            asset_id=asset_id,
            status='COMPLETED',
            completed_at__gte=start_date,
            completed_at__lte=end_date,
            actual_hours__isnull=False
        ).aggregate(
            total_downtime=Sum('actual_hours')
        )['total_downtime'] or 0
        
        availability = ((total_hours - downtime_wo) / total_hours * 100) if total_hours > 0 else 0
        
        # Simplified OEE (only availability component)
        oee = availability
        
        return {
            'asset_id': str(asset_id),
            'period_hours': total_hours,
            'downtime_hours': downtime_wo,
            'availability': round(availability, 2),
            'oee': round(oee, 2)
        }


class WorkOrderReportService:
    """Service for work order reports"""
    
    @staticmethod
    def generate_summary_report(start_date=None, end_date=None):
        """Generate work order summary report"""
        filters = Q()
        
        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)
        
        work_orders = WorkOrder.objects.filter(filters)
        
        summary = {
            'total': work_orders.count(),
            'by_status': dict(work_orders.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_priority': dict(work_orders.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'by_type': dict(work_orders.values('work_order_type').annotate(count=Count('id')).values_list('work_order_type', 'count')),
            'avg_completion_hours': work_orders.filter(status='COMPLETED', actual_hours__isnull=False).aggregate(avg=Avg('actual_hours'))['avg'] or 0,
            'total_hours': work_orders.filter(actual_hours__isnull=False).aggregate(total=Sum('actual_hours'))['total'] or 0
        }
        
        return summary



class AssetDowntimeReportService:
    """Service for asset downtime reports"""
    
    @staticmethod
    def generate_downtime_report(start_date=None, end_date=None):
        """Generate asset downtime report"""
        filters = Q(status='COMPLETED', actual_hours__isnull=False)
        
        if start_date:
            filters &= Q(completed_at__gte=start_date)
        if end_date:
            filters &= Q(completed_at__lte=end_date)
        
        downtime_by_asset = WorkOrder.objects.filter(filters).values(
            'asset__id',
            'asset__name',
            'asset__asset_code',
            'asset__vehicle_type'
        ).annotate(
            total_downtime_hours=Sum('actual_hours'),
            work_order_count=Count('id'),
            avg_downtime_hours=Avg('actual_hours')
        ).order_by('-total_downtime_hours')
        
        return list(downtime_by_asset)


class SparePartConsumptionReportService:
    """Service for spare part consumption reports"""
    
    @staticmethod
    def generate_consumption_report(start_date=None, end_date=None):
        """Generate spare part consumption report"""
        filters = Q(movement_type='OUT')
        
        if start_date:
            filters &= Q(created_at__gte=start_date)
        if end_date:
            filters &= Q(created_at__lte=end_date)
        
        consumption = StockMovement.objects.filter(filters).values(
            'spare_part__id',
            'spare_part__name',
            'spare_part__part_number',
            'spare_part__unit_cost'
        ).annotate(
            total_quantity=Sum('quantity'),
            movement_count=Count('id')
        ).annotate(
            total_cost=ExpressionWrapper(
                F('total_quantity') * F('spare_part__unit_cost'),
                output_field=F('spare_part__unit_cost').field
            )
        ).order_by('-total_quantity')
        
        # Calculate totals
        totals = StockMovement.objects.filter(filters).aggregate(
            total_movements=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        return {
            'consumption_by_part': list(consumption),
            'totals': totals
        }


class ReportScheduler:
    """Service for scheduling reports"""
    
    @staticmethod
    def schedule_report(report_type, frequency, recipients, parameters=None):
        """Schedule a report for automatic generation"""
        # This would integrate with Cloud Scheduler or Celery
        # For now, return a placeholder
        return {
            'report_type': report_type,
            'frequency': frequency,
            'recipients': recipients,
            'parameters': parameters or {},
            'status': 'scheduled'
        }
