"""
Views for image processing API endpoints.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone

from apps.images.models import (
    InspectionPhoto,
    ImageAnalysisResult,
    VisualAnomaly,
    MeterReading,
    DamageReport
)
from apps.images.serializers import (
    InspectionPhotoSerializer,
    InspectionPhotoDetailSerializer,
    InspectionPhotoUploadSerializer,
    ImageAnalysisResultSerializer,
    VisualAnomalySerializer,
    MeterReadingSerializer,
    DamageReportSerializer
)
from apps.images.services.image_processing_service import image_processing_service
from apps.images.services.image_analysis_service import image_analysis_service
from apps.assets.models import Asset
from apps.work_orders.models import WorkOrder
from apps.checklists.models import ChecklistResponse

logger = logging.getLogger(__name__)

# Import Celery tasks
try:
    from apps.images.tasks import process_inspection_photo, batch_process_images
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not available, will use synchronous processing")


class InspectionPhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inspection photos.
    Provides upload, list, retrieve, and delete operations.
    """
    queryset = InspectionPhoto.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'upload':
            return InspectionPhotoUploadSerializer
        elif self.action == 'retrieve':
            return InspectionPhotoDetailSerializer
        return InspectionPhotoSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role and query parameters."""
        queryset = InspectionPhoto.objects.select_related(
            'asset', 'work_order', 'checklist_response', 'uploaded_by'
        ).prefetch_related(
            'anomalies', 'meter_readings', 'damage_reports'
        )
        
        # Filter by asset if provided
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by work order if provided
        work_order_id = self.request.query_params.get('work_order_id')
        if work_order_id:
            queryset = queryset.filter(work_order_id=work_order_id)
        
        # Filter by processing status if provided
        processing_status = self.request.query_params.get('processing_status')
        if processing_status:
            queryset = queryset.filter(processing_status=processing_status)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(captured_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(captured_at__lte=date_to)
        
        return queryset.order_by('-captured_at')
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def upload(self, request):
        """
        Upload and process an inspection photo.
        
        Request body:
        - image: Image file (required)
        - asset_id: UUID of the asset (required)
        - work_order_id: UUID of work order (optional)
        - checklist_response_id: UUID of checklist response (optional)
        
        Returns:
        - 201: Photo uploaded successfully with metadata
        - 400: Validation error
        - 500: Processing error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image_file = serializer.validated_data['image']
        asset_id = serializer.validated_data['asset_id']
        work_order_id = serializer.validated_data.get('work_order_id')
        checklist_response_id = serializer.validated_data.get('checklist_response_id')
        
        try:
            # Get related objects
            asset = Asset.objects.get(id=asset_id)
            work_order = WorkOrder.objects.get(id=work_order_id) if work_order_id else None
            checklist_response = ChecklistResponse.objects.get(id=checklist_response_id) if checklist_response_id else None
            
            # Process and upload image
            result = image_processing_service.process_and_upload(
                image_file,
                str(asset_id),
                str(request.user.id)
            )
            
            # Create InspectionPhoto record
            photo = InspectionPhoto.objects.create(
                asset=asset,
                work_order=work_order,
                checklist_response=checklist_response,
                original_url=result['original_url'],
                thumbnail_url=result['thumbnail_url'],
                file_size=result['file_size'],
                width=result['width'],
                height=result['height'],
                format=result['format'],
                captured_at=result['captured_at'],
                gps_latitude=result.get('gps_latitude'),
                gps_longitude=result.get('gps_longitude'),
                gps_altitude=result.get('gps_altitude'),
                compass_heading=result.get('compass_heading'),
                device_info=result.get('device_info', {}),
                processing_status=InspectionPhoto.STATUS_PENDING,
                uploaded_by=request.user
            )
            
            # Trigger async analysis with Celery (or sync if Celery not available)
            if CELERY_AVAILABLE:
                # Async processing with Celery
                logger.info(f"Triggering async analysis for photo {photo.id}")
                process_inspection_photo.delay(str(photo.id))
                logger.info(f"Photo uploaded successfully: {photo.id}, analysis queued")
            else:
                # Fallback to synchronous processing
                try:
                    if image_analysis_service.is_available():
                        logger.info(f"Starting synchronous Vision AI analysis for photo {photo.id}")
                        image_analysis_service.analyze_inspection_photo(photo)
                    else:
                        logger.warning("Vision AI not available, skipping analysis")
                except Exception as analysis_error:
                    logger.error(f"Analysis failed but photo uploaded: {str(analysis_error)}")
                    # Don't fail the upload if analysis fails
                
                logger.info(f"Photo uploaded successfully: {photo.id}")
            
            # Return created photo (analysis may still be pending if async)
            response_serializer = InspectionPhotoSerializer(photo)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except WorkOrder.DoesNotExist:
            return Response(
                {'error': 'Work order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ChecklistResponse.DoesNotExist:
            return Response(
                {'error': 'Checklist response not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error uploading photo: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to process image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """
        Reprocess an existing photo (re-run analysis).
        
        Returns:
        - 200: Reprocessing completed
        - 404: Photo not found
        - 500: Analysis failed
        """
        photo = self.get_object()
        
        try:
            # Delete existing analysis results
            if hasattr(photo, 'analysis_result'):
                photo.analysis_result.delete()
            
            # Trigger analysis
            if image_analysis_service.is_available():
                logger.info(f"Reprocessing photo {photo.id}")
                result = image_analysis_service.analyze_inspection_photo(photo)
                
                # Return updated photo with new analysis
                response_serializer = InspectionPhotoDetailSerializer(photo)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Vision AI not available'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
                
        except Exception as e:
            logger.error(f"Error reprocessing photo: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Reprocessing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def batch_analyze(self, request):
        """
        Analyze multiple photos in batch using Celery.
        
        Request body:
        - photo_ids: List of photo UUIDs
        
        Returns:
        - Batch analysis results with task info
        """
        photo_ids = request.data.get('photo_ids', [])
        
        if not photo_ids:
            return Response(
                {'error': 'photo_ids list is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not image_analysis_service.is_available():
            return Response(
                {'error': 'Vision AI not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            if CELERY_AVAILABLE:
                # Use Celery for async batch processing
                result = batch_process_images.delay(photo_ids)
                
                return Response({
                    'status': 'batch_queued',
                    'total_photos': len(photo_ids),
                    'task_id': result.id,
                    'message': 'Batch processing queued. Check task status for results.'
                }, status=status.HTTP_202_ACCEPTED)
            else:
                # Fallback to synchronous batch processing
                results = image_analysis_service.analyze_batch(photo_ids)
                return Response(results, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Batch analysis error: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Batch analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='task-status/(?P<task_id>[^/.]+)')
    def task_status(self, request, task_id=None):
        """
        Get status of a Celery task.
        
        Args:
            task_id: Celery task ID
            
        Returns:
        - Task status and result
        """
        if not CELERY_AVAILABLE:
            return Response(
                {'error': 'Celery not available'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            from celery.result import AsyncResult
            
            task = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task.state,
                'ready': task.ready(),
                'successful': task.successful() if task.ready() else None,
            }
            
            if task.ready():
                if task.successful():
                    response_data['result'] = task.result
                else:
                    response_data['error'] = str(task.info)
            else:
                # Task is still pending or running
                if task.state == 'PROGRESS':
                    response_data['progress'] = task.info
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
            return Response(
                {'error': f'Failed to get task status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get statistics about inspection photos.
        
        Returns:
        - total_photos: Total number of photos
        - photos_by_status: Count by processing status
        - photos_with_anomalies: Count of photos with detected anomalies
        - photos_with_gps: Count of photos with GPS data
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_photos': queryset.count(),
            'photos_by_status': {},
            'photos_with_anomalies': queryset.filter(
                analysis_result__anomalies_detected=True
            ).count(),
            'photos_with_gps': queryset.filter(
                gps_latitude__isnull=False,
                gps_longitude__isnull=False
            ).count(),
        }
        
        # Count by status
        for status_choice in InspectionPhoto.STATUS_CHOICES:
            status_value = status_choice[0]
            count = queryset.filter(processing_status=status_value).count()
            stats['photos_by_status'][status_value] = count
        
        return Response(stats)


class ImageAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing image analysis results.
    Read-only - results are created by background tasks.
    """
    queryset = ImageAnalysisResult.objects.all()
    serializer_class = ImageAnalysisResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = ImageAnalysisResult.objects.select_related('photo')
        
        # Filter by photo
        photo_id = self.request.query_params.get('photo_id')
        if photo_id:
            queryset = queryset.filter(photo_id=photo_id)
        
        # Filter by anomalies detected
        has_anomalies = self.request.query_params.get('has_anomalies')
        if has_anomalies is not None:
            queryset = queryset.filter(anomalies_detected=has_anomalies.lower() == 'true')
        
        # Filter by damage type
        damage_type = self.request.query_params.get('damage_type')
        if damage_type:
            queryset = queryset.filter(damage_type=damage_type)
        
        return queryset.order_by('-created_at')


class VisualAnomalyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing visual anomalies.
    Allows viewing, updating feedback, and creating work orders.
    """
    queryset = VisualAnomaly.objects.all()
    serializer_class = VisualAnomalySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = VisualAnomaly.objects.select_related(
            'photo', 'photo__asset', 'analysis_result', 'work_order_created'
        )
        
        # Filter by anomaly type
        anomaly_type = self.request.query_params.get('anomaly_type')
        if anomaly_type:
            queryset = queryset.filter(anomaly_type=anomaly_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(photo__asset_id=asset_id)
        
        # Filter by confirmation status
        confirmed = self.request.query_params.get('confirmed')
        if confirmed is not None:
            if confirmed.lower() == 'true':
                queryset = queryset.filter(confirmed_by_user=True)
            elif confirmed.lower() == 'false':
                queryset = queryset.filter(confirmed_by_user=False)
            else:
                queryset = queryset.filter(confirmed_by_user__isnull=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm or reject an anomaly detection.
        
        Request body:
        - confirmed: boolean (true/false)
        - feedback: string (optional)
        """
        anomaly = self.get_object()
        
        confirmed = request.data.get('confirmed')
        feedback = request.data.get('feedback', '')
        
        if confirmed is None:
            return Response(
                {'error': 'confirmed field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        anomaly.confirmed_by_user = confirmed
        anomaly.user_feedback = feedback
        anomaly.feedback_by = request.user
        anomaly.feedback_at = timezone.now()
        anomaly.save()
        
        logger.info(f"Anomaly {anomaly.id} {'confirmed' if confirmed else 'rejected'} by {request.user}")
        
        serializer = self.get_serializer(anomaly)
        return Response(serializer.data)


class MeterReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing meter readings.
    Allows viewing, validating, and correcting OCR results.
    """
    queryset = MeterReading.objects.all()
    serializer_class = MeterReadingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = MeterReading.objects.select_related('photo', 'asset')
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by reading type
        reading_type = self.request.query_params.get('reading_type')
        if reading_type:
            queryset = queryset.filter(reading_type=reading_type)
        
        # Filter by outliers
        outliers_only = self.request.query_params.get('outliers_only')
        if outliers_only and outliers_only.lower() == 'true':
            queryset = queryset.filter(is_outlier=True)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Validate or correct a meter reading.
        
        Request body:
        - is_valid: boolean
        - corrected_value: decimal (optional)
        - notes: string (optional)
        """
        reading = self.get_object()
        
        is_valid = request.data.get('is_valid')
        corrected_value = request.data.get('corrected_value')
        notes = request.data.get('notes', '')
        
        if is_valid is None:
            return Response(
                {'error': 'is_valid field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reading.is_valid = is_valid
        if corrected_value is not None:
            reading.value = corrected_value
        reading.validation_notes = notes
        reading.validated_by = request.user
        reading.validated_at = timezone.now()
        reading.save()
        
        logger.info(f"Meter reading {reading.id} validated by {request.user}")
        
        serializer = self.get_serializer(reading)
        return Response(serializer.data)


class DamageReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing damage reports.
    Allows viewing, updating, and resolving damage reports.
    """
    queryset = DamageReport.objects.all()
    serializer_class = DamageReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = DamageReport.objects.select_related(
            'photo', 'asset', 'work_order', 'resolved_by'
        )
        
        # Filter by asset
        asset_id = self.request.query_params.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        
        # Filter by damage type
        damage_type = self.request.query_params.get('damage_type')
        if damage_type:
            queryset = queryset.filter(damage_type=damage_type)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by status
        report_status = self.request.query_params.get('status')
        if report_status:
            queryset = queryset.filter(status=report_status)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark a damage report as resolved.
        
        Request body:
        - resolution_notes: string (optional)
        """
        report = self.get_object()
        
        resolution_notes = request.data.get('resolution_notes', '')
        
        report.status = DamageReport.STATUS_RESOLVED
        report.resolved_at = timezone.now()
        report.resolved_by = request.user
        if resolution_notes:
            report.user_notes = f"{report.user_notes}\n\nResolution: {resolution_notes}"
        report.save()
        
        logger.info(f"Damage report {report.id} resolved by {request.user}")
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)
