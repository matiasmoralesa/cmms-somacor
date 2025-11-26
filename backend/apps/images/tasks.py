"""
Celery tasks for image processing.
Handles asynchronous image analysis, anomaly detection, and batch operations.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import shared_task, group, chord
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.conf import settings

from apps.images.models import InspectionPhoto, ImageAnalysisResult
from apps.images.services.image_analysis_service import image_analysis_service

logger = logging.getLogger(__name__)


# ============================================================================
# HIGH PRIORITY TASKS - Critical image analysis
# ============================================================================

@shared_task(
    bind=True,
    name='apps.images.tasks.process_inspection_photo',
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # 10 minutes
    retry_jitter=True,
    queue='high_priority'
)
def process_inspection_photo(self, photo_id: str) -> Dict[str, Any]:
    """
    Process an inspection photo with Vision AI analysis.
    
    This is the main task for analyzing uploaded photos.
    Runs in high_priority queue for fast processing.
    
    Args:
        photo_id: UUID of the InspectionPhoto
        
    Returns:
        Dict with analysis results
        
    Raises:
        Exception: If analysis fails after retries
    """
    try:
        logger.info(f"Starting analysis for photo {photo_id}")
        
        # Get photo
        photo = InspectionPhoto.objects.get(id=photo_id)
        
        # Check if already processed
        if photo.processing_status == InspectionPhoto.STATUS_COMPLETED:
            logger.info(f"Photo {photo_id} already processed, skipping")
            return {'status': 'already_processed', 'photo_id': photo_id}
        
        # Perform analysis
        result = image_analysis_service.analyze_inspection_photo(photo)
        
        logger.info(f"Analysis completed for photo {photo_id}")
        
        return {
            'status': 'success',
            'photo_id': photo_id,
            'result_id': str(result.id),
            'anomalies_detected': result.anomalies_detected,
            'processing_time_ms': result.processing_time_ms
        }
        
    except InspectionPhoto.DoesNotExist:
        logger.error(f"Photo {photo_id} not found")
        return {'status': 'error', 'photo_id': photo_id, 'error': 'Photo not found'}
        
    except Exception as exc:
        logger.error(f"Error processing photo {photo_id}: {str(exc)}", exc_info=True)
        
        # Update photo status
        try:
            photo = InspectionPhoto.objects.get(id=photo_id)
            photo.processing_status = InspectionPhoto.STATUS_FAILED
            photo.processing_error = str(exc)
            photo.save()
        except:
            pass
        
        # Retry with exponential backoff
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for photo {photo_id}")
            return {'status': 'failed', 'photo_id': photo_id, 'error': str(exc)}


@shared_task(
    bind=True,
    name='apps.images.tasks.analyze_critical_anomaly',
    max_retries=3,
    queue='high_priority'
)
def analyze_critical_anomaly(self, anomaly_id: str) -> Dict[str, Any]:
    """
    Analyze a critical anomaly and create work order if needed.
    
    Args:
        anomaly_id: UUID of the VisualAnomaly
        
    Returns:
        Dict with analysis results
    """
    try:
        from apps.images.models import VisualAnomaly
        from apps.work_orders.models import WorkOrder
        
        anomaly = VisualAnomaly.objects.get(id=anomaly_id)
        
        # Check if work order already created
        if anomaly.work_order_created:
            logger.info(f"Work order already exists for anomaly {anomaly_id}")
            return {'status': 'work_order_exists', 'anomaly_id': anomaly_id}
        
        # Create work order for critical anomaly
        if anomaly.is_critical():
            work_order = WorkOrder.objects.create(
                title=f"Critical Anomaly: {anomaly.get_anomaly_type_display()}",
                description=f"Critical anomaly detected on {anomaly.photo.asset.name}. "
                           f"Type: {anomaly.get_anomaly_type_display()}, "
                           f"Confidence: {anomaly.confidence:.0%}. "
                           f"Location: {anomaly.bounding_box}",
                asset=anomaly.photo.asset,
                work_order_type=WorkOrder.TYPE_CORRECTIVE,
                priority=WorkOrder.PRIORITY_URGENT,
                created_by=anomaly.photo.uploaded_by
            )
            
            anomaly.work_order_created = work_order
            anomaly.save()
            
            logger.info(f"Created work order {work_order.work_order_number} for anomaly {anomaly_id}")
            
            return {
                'status': 'work_order_created',
                'anomaly_id': anomaly_id,
                'work_order_id': str(work_order.id),
                'work_order_number': work_order.work_order_number
            }
        
        return {'status': 'not_critical', 'anomaly_id': anomaly_id}
        
    except Exception as exc:
        logger.error(f"Error analyzing critical anomaly {anomaly_id}: {str(exc)}")
        raise self.retry(exc=exc)


# ============================================================================
# NORMAL PRIORITY TASKS - Standard processing
# ============================================================================

@shared_task(
    name='apps.images.tasks.analyze_anomalies',
    queue='normal'
)
def analyze_anomalies(photo_id: str) -> Dict[str, Any]:
    """
    Analyze anomalies in a photo (placeholder for ML model in Task 4).
    
    Args:
        photo_id: UUID of the InspectionPhoto
        
    Returns:
        Dict with anomaly analysis results
    """
    logger.info(f"Analyzing anomalies for photo {photo_id}")
    # Will be implemented in Task 4 with ML model
    return {'status': 'pending_ml_model', 'photo_id': photo_id}


@shared_task(
    name='apps.images.tasks.extract_text_ocr',
    queue='normal'
)
def extract_text_ocr(photo_id: str) -> Dict[str, Any]:
    """
    Extract text from photo using OCR (placeholder for enhanced OCR in Task 5).
    
    Args:
        photo_id: UUID of the InspectionPhoto
        
    Returns:
        Dict with OCR results
    """
    logger.info(f"Extracting text from photo {photo_id}")
    # Will be enhanced in Task 5 with ML classification
    return {'status': 'pending_ml_model', 'photo_id': photo_id}


@shared_task(
    name='apps.images.tasks.classify_damage',
    queue='normal'
)
def classify_damage(photo_id: str) -> Dict[str, Any]:
    """
    Classify damage type in photo (placeholder for ML model in Task 6).
    
    Args:
        photo_id: UUID of the InspectionPhoto
        
    Returns:
        Dict with damage classification results
    """
    logger.info(f"Classifying damage for photo {photo_id}")
    # Will be implemented in Task 6 with ML model
    return {'status': 'pending_ml_model', 'photo_id': photo_id}


@shared_task(
    name='apps.images.tasks.generate_image_report',
    queue='normal'
)
def generate_image_report(photo_id: str) -> Dict[str, Any]:
    """
    Generate comprehensive report for analyzed photo.
    
    Args:
        photo_id: UUID of the InspectionPhoto
        
    Returns:
        Dict with report generation results
    """
    try:
        photo = InspectionPhoto.objects.get(id=photo_id)
        
        # Check if analysis is complete
        if not hasattr(photo, 'analysis_result'):
            return {'status': 'no_analysis', 'photo_id': photo_id}
        
        result = photo.analysis_result
        
        # Generate report summary
        report = {
            'photo_id': photo_id,
            'asset': photo.asset.name,
            'captured_at': photo.captured_at.isoformat(),
            'analysis_summary': result.get_summary(),
            'anomalies_count': photo.anomalies.count(),
            'meter_readings_count': photo.meter_readings.count(),
            'damage_reports_count': photo.damage_reports.count(),
        }
        
        logger.info(f"Generated report for photo {photo_id}")
        
        return {'status': 'success', 'report': report}
        
    except Exception as exc:
        logger.error(f"Error generating report for photo {photo_id}: {str(exc)}")
        return {'status': 'error', 'photo_id': photo_id, 'error': str(exc)}


# ============================================================================
# BATCH PROCESSING TASKS - Non-urgent bulk operations
# ============================================================================

@shared_task(
    name='apps.images.tasks.batch_process_images',
    queue='batch'
)
def batch_process_images(photo_ids: List[str]) -> Dict[str, Any]:
    """
    Process multiple photos in batch.
    
    Args:
        photo_ids: List of InspectionPhoto UUIDs
        
    Returns:
        Dict with batch processing results
    """
    logger.info(f"Starting batch processing of {len(photo_ids)} photos")
    
    # Create a group of tasks
    job = group(process_inspection_photo.s(photo_id) for photo_id in photo_ids)
    result = job.apply_async()
    
    return {
        'status': 'batch_started',
        'total_photos': len(photo_ids),
        'group_id': result.id
    }


@shared_task(
    name='apps.images.tasks.generate_comparison_report',
    queue='batch'
)
def generate_comparison_report(asset_id: str, date_from: str, date_to: str) -> Dict[str, Any]:
    """
    Generate comparison report for an asset over time.
    
    Args:
        asset_id: UUID of the Asset
        date_from: Start date (ISO format)
        date_to: End date (ISO format)
        
    Returns:
        Dict with comparison report
    """
    try:
        from apps.assets.models import Asset
        
        asset = Asset.objects.get(id=asset_id)
        
        # Get photos in date range
        photos = InspectionPhoto.objects.filter(
            asset=asset,
            captured_at__gte=date_from,
            captured_at__lte=date_to,
            processing_status=InspectionPhoto.STATUS_COMPLETED
        ).order_by('captured_at')
        
        # Generate comparison data
        comparison = {
            'asset_id': asset_id,
            'asset_name': asset.name,
            'date_range': {'from': date_from, 'to': date_to},
            'total_photos': photos.count(),
            'anomalies_trend': [],
            'damage_progression': []
        }
        
        # Analyze trends
        for photo in photos:
            if hasattr(photo, 'analysis_result'):
                comparison['anomalies_trend'].append({
                    'date': photo.captured_at.isoformat(),
                    'anomalies_detected': photo.analysis_result.anomalies_detected,
                    'anomaly_count': photo.anomalies.count()
                })
        
        logger.info(f"Generated comparison report for asset {asset_id}")
        
        return {'status': 'success', 'comparison': comparison}
        
    except Exception as exc:
        logger.error(f"Error generating comparison report: {str(exc)}")
        return {'status': 'error', 'error': str(exc)}


@shared_task(
    name='apps.images.tasks.archive_old_messages',
    queue='batch'
)
def archive_old_messages() -> Dict[str, Any]:
    """
    Archive chat messages older than 90 days.
    Scheduled to run daily at 2 AM.
    
    Returns:
        Dict with archival results
    """
    logger.info("Starting archival of old messages")
    
    # Will be implemented in Task 8 (Chat System)
    # For now, just log
    
    return {'status': 'pending_chat_implementation'}


@shared_task(
    name='apps.images.tasks.cleanup_old_images',
    queue='batch'
)
def cleanup_old_images() -> Dict[str, Any]:
    """
    Cleanup old cached image analysis results.
    Scheduled to run weekly on Sunday at 3 AM.
    
    Returns:
        Dict with cleanup results
    """
    logger.info("Starting cleanup of old cached images")
    
    try:
        # Delete expired cached results
        cutoff_date = timezone.now()
        expired_results = ImageAnalysisResult.objects.filter(
            cached_result=True,
            cache_expires_at__lt=cutoff_date
        )
        
        count = expired_results.count()
        expired_results.delete()
        
        logger.info(f"Deleted {count} expired cached results")
        
        return {'status': 'success', 'deleted_count': count}
        
    except Exception as exc:
        logger.error(f"Error cleaning up old images: {str(exc)}")
        return {'status': 'error', 'error': str(exc)}


@shared_task(
    name='apps.images.tasks.generate_daily_analytics',
    queue='batch'
)
def generate_daily_analytics() -> Dict[str, Any]:
    """
    Generate daily analytics report.
    Scheduled to run daily at 6 AM.
    
    Returns:
        Dict with analytics data
    """
    logger.info("Generating daily analytics")
    
    try:
        yesterday = timezone.now() - timedelta(days=1)
        
        # Count photos processed yesterday
        photos_processed = InspectionPhoto.objects.filter(
            processed_at__gte=yesterday,
            processing_status=InspectionPhoto.STATUS_COMPLETED
        ).count()
        
        # Count anomalies detected
        from apps.images.models import VisualAnomaly
        anomalies_detected = VisualAnomaly.objects.filter(
            created_at__gte=yesterday
        ).count()
        
        # Count critical anomalies
        critical_anomalies = VisualAnomaly.objects.filter(
            created_at__gte=yesterday,
            severity=VisualAnomaly.SEVERITY_CRITICAL
        ).count()
        
        analytics = {
            'date': yesterday.date().isoformat(),
            'photos_processed': photos_processed,
            'anomalies_detected': anomalies_detected,
            'critical_anomalies': critical_anomalies
        }
        
        logger.info(f"Daily analytics: {analytics}")
        
        return {'status': 'success', 'analytics': analytics}
        
    except Exception as exc:
        logger.error(f"Error generating daily analytics: {str(exc)}")
        return {'status': 'error', 'error': str(exc)}


@shared_task(
    name='apps.images.tasks.check_budget_usage',
    queue='batch'
)
def check_budget_usage() -> Dict[str, Any]:
    """
    Check Vision AI budget usage and send alerts if needed.
    Scheduled to run every 6 hours.
    
    Returns:
        Dict with budget status
    """
    logger.info("Checking budget usage")
    
    try:
        # Count Vision AI calls this month
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0)
        
        vision_ai_calls = ImageAnalysisResult.objects.filter(
            created_at__gte=first_day_of_month,
            vision_ai_used=True,
            cached_result=False
        ).count()
        
        # Estimate cost (simplified)
        # Vision AI: $1.50 per 1000 images after first 1000 free
        free_tier = 1000
        if vision_ai_calls > free_tier:
            estimated_cost = ((vision_ai_calls - free_tier) / 1000) * 1.50
        else:
            estimated_cost = 0
        
        budget_limit = settings.MONTHLY_BUDGET_LIMIT_USD
        usage_percentage = (estimated_cost / budget_limit) * 100 if budget_limit > 0 else 0
        
        budget_status = {
            'month': timezone.now().strftime('%Y-%m'),
            'vision_ai_calls': vision_ai_calls,
            'estimated_cost_usd': round(estimated_cost, 2),
            'budget_limit_usd': budget_limit,
            'usage_percentage': round(usage_percentage, 2)
        }
        
        # Send alert if approaching limit
        if usage_percentage >= settings.BUDGET_WARNING_THRESHOLD * 100:
            logger.warning(f"Budget usage at {usage_percentage:.1f}%: ${estimated_cost:.2f} / ${budget_limit}")
        
        return {'status': 'success', 'budget': budget_status}
        
    except Exception as exc:
        logger.error(f"Error checking budget usage: {str(exc)}")
        return {'status': 'error', 'error': str(exc)}


# ============================================================================
# ML TRAINING TASKS - Long-running model training
# ============================================================================

@shared_task(
    name='apps.images.tasks.retrain_anomaly_model',
    queue='ml_training',
    time_limit=7200  # 2 hours
)
def retrain_anomaly_model() -> Dict[str, Any]:
    """
    Retrain anomaly detection model with new data.
    Will be implemented in Task 4.
    
    Returns:
        Dict with training results
    """
    logger.info("Retraining anomaly detection model")
    # Will be implemented in Task 4
    return {'status': 'pending_ml_implementation'}


@shared_task(
    name='apps.images.tasks.retrain_damage_model',
    queue='ml_training',
    time_limit=7200  # 2 hours
)
def retrain_damage_model() -> Dict[str, Any]:
    """
    Retrain damage classification model with new data.
    Will be implemented in Task 6.
    
    Returns:
        Dict with training results
    """
    logger.info("Retraining damage classification model")
    # Will be implemented in Task 6
    return {'status': 'pending_ml_implementation'}


@shared_task(
    name='apps.images.tasks.evaluate_model_performance',
    queue='ml_training'
)
def evaluate_model_performance() -> Dict[str, Any]:
    """
    Evaluate ML model performance metrics.
    Will be implemented in Task 14.
    
    Returns:
        Dict with evaluation results
    """
    logger.info("Evaluating model performance")
    # Will be implemented in Task 14
    return {'status': 'pending_ml_implementation'}
