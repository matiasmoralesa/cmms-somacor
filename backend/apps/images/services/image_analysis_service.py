"""
Image analysis service that integrates Vision AI with the image processing pipeline.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

from apps.images.models import (
    InspectionPhoto,
    ImageAnalysisResult,
    VisualAnomaly,
    MeterReading
)
from apps.images.services.vision_ai_client import vision_ai_client

logger = logging.getLogger(__name__)


class ImageAnalysisService:
    """
    Service for analyzing images using Google Cloud Vision AI.
    Coordinates between Vision AI client and database models.
    """
    
    def __init__(self):
        """Initialize image analysis service."""
        self.vision_client = vision_ai_client
    
    def is_available(self) -> bool:
        """Check if Vision AI is available."""
        return self.vision_client.is_available()
    
    # ========================================================================
    # MAIN ANALYSIS PIPELINE
    # ========================================================================
    
    def analyze_inspection_photo(self, photo: InspectionPhoto) -> ImageAnalysisResult:
        """
        Perform complete analysis on an inspection photo.
        
        Args:
            photo: InspectionPhoto instance
            
        Returns:
            ImageAnalysisResult instance
            
        Raises:
            RuntimeError: If Vision AI is not available
            Exception: If analysis fails
        """
        if not self.is_available():
            raise RuntimeError("Vision AI is not available")
        
        start_time = datetime.now()
        
        try:
            # Update photo status
            photo.processing_status = InspectionPhoto.STATUS_PROCESSING
            photo.save()
            
            # Check if we have cached results
            cached_result = self._check_cache(photo.original_url)
            if cached_result:
                logger.info(f"Using cached results for photo {photo.id}")
                result = self._create_result_from_cache(photo, cached_result)
                photo.processing_status = InspectionPhoto.STATUS_COMPLETED
                photo.processed_at = timezone.now()
                photo.save()
                return result
            
            # Perform comprehensive analysis
            logger.info(f"Starting Vision AI analysis for photo {photo.id}")
            analysis_data = self.vision_client.analyze_image_comprehensive(photo.original_url)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create analysis result
            result = self._create_analysis_result(photo, analysis_data, processing_time)
            
            # Extract specific data
            self._extract_anomalies(photo, result, analysis_data)
            self._extract_meter_readings(photo, result, analysis_data)
            
            # Update photo status
            photo.processing_status = InspectionPhoto.STATUS_COMPLETED
            photo.processed_at = timezone.now()
            photo.save()
            
            logger.info(f"Analysis completed for photo {photo.id} in {processing_time}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing photo {photo.id}: {str(e)}", exc_info=True)
            
            # Update photo with error
            photo.processing_status = InspectionPhoto.STATUS_FAILED
            photo.processing_error = str(e)
            photo.save()
            
            raise
    
    # ========================================================================
    # RESULT CREATION
    # ========================================================================
    
    def _create_analysis_result(self, photo: InspectionPhoto, 
                               analysis_data: Dict[str, Any],
                               processing_time: int) -> ImageAnalysisResult:
        """Create ImageAnalysisResult from Vision AI data."""
        
        # Determine if anomalies were detected (basic heuristic)
        anomalies_detected = self._detect_anomalies_heuristic(analysis_data)
        
        # Create result
        result = ImageAnalysisResult.objects.create(
            photo=photo,
            labels=analysis_data.get('labels', []),
            detected_objects=analysis_data.get('objects', []),
            text_annotations=analysis_data.get('texts', []),
            dominant_colors=analysis_data.get('dominant_colors', []),
            safe_search=analysis_data.get('safe_search', {}),
            anomalies_detected=anomalies_detected,
            processing_time_ms=processing_time,
            model_version='vision-ai-v1',
            vision_ai_used=True,
            cached_result=False,
            cache_expires_at=timezone.now() + timedelta(days=settings.VISION_AI_CACHE_DAYS)
        )
        
        logger.info(f"Created analysis result {result.id} for photo {photo.id}")
        
        return result
    
    def _detect_anomalies_heuristic(self, analysis_data: Dict[str, Any]) -> bool:
        """
        Basic heuristic to detect potential anomalies from Vision AI labels.
        This is a simple implementation - will be enhanced with ML models in Task 4.
        """
        anomaly_keywords = [
            'rust', 'corrosion', 'crack', 'damage', 'broken', 'leak',
            'wear', 'tear', 'dent', 'scratch', 'hole', 'missing'
        ]
        
        labels = analysis_data.get('labels', [])
        for label in labels:
            description = label.get('description', '').lower()
            if any(keyword in description for keyword in anomaly_keywords):
                return True
        
        return False
    
    # ========================================================================
    # ANOMALY EXTRACTION
    # ========================================================================
    
    def _extract_anomalies(self, photo: InspectionPhoto, 
                          result: ImageAnalysisResult,
                          analysis_data: Dict[str, Any]):
        """
        Extract and create VisualAnomaly records from analysis data.
        This is a basic implementation - will be enhanced with ML models in Task 4.
        """
        anomaly_keywords = {
            'rust': VisualAnomaly.TYPE_CORROSION,
            'corrosion': VisualAnomaly.TYPE_CORROSION,
            'crack': VisualAnomaly.TYPE_CRACK,
            'leak': VisualAnomaly.TYPE_LEAK,
            'wear': VisualAnomaly.TYPE_WEAR,
            'dent': VisualAnomaly.TYPE_DEFORMATION,
            'damage': VisualAnomaly.TYPE_OTHER,
        }
        
        detected_objects = analysis_data.get('objects', [])
        
        for obj in detected_objects:
            name = obj.get('name', '').lower()
            score = obj.get('score', 0)
            bounding_box = obj.get('bounding_box', [])
            
            # Check if object name contains anomaly keywords
            anomaly_type = None
            for keyword, anom_type in anomaly_keywords.items():
                if keyword in name:
                    anomaly_type = anom_type
                    break
            
            if anomaly_type and score >= settings.ANOMALY_DETECTION_THRESHOLD:
                # Determine severity based on confidence
                if score >= 0.90:
                    severity = VisualAnomaly.SEVERITY_CRITICAL
                elif score >= 0.80:
                    severity = VisualAnomaly.SEVERITY_HIGH
                elif score >= 0.70:
                    severity = VisualAnomaly.SEVERITY_MEDIUM
                else:
                    severity = VisualAnomaly.SEVERITY_LOW
                
                # Convert bounding box to our format
                bbox = self._convert_bounding_box(bounding_box)
                
                # Create anomaly
                anomaly = VisualAnomaly.objects.create(
                    photo=photo,
                    analysis_result=result,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    confidence=score,
                    bounding_box=bbox,
                    description=f"Detected {name} with {score:.0%} confidence"
                )
                
                logger.info(f"Created anomaly {anomaly.id}: {anomaly_type} - {severity}")
                
                # Send alert if critical
                if anomaly.is_critical():
                    self._send_anomaly_alert(anomaly)
    
    def _convert_bounding_box(self, vertices: list) -> Dict[str, float]:
        """Convert Vision AI bounding box format to our format."""
        if not vertices or len(vertices) < 2:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        # Vision AI returns normalized coordinates (0-1)
        x_coords = [v.get('x', 0) for v in vertices]
        y_coords = [v.get('y', 0) for v in vertices]
        
        x_min = min(x_coords)
        y_min = min(y_coords)
        x_max = max(x_coords)
        y_max = max(y_coords)
        
        return {
            'x': x_min,
            'y': y_min,
            'width': x_max - x_min,
            'height': y_max - y_min
        }
    
    def _send_anomaly_alert(self, anomaly: VisualAnomaly):
        """Send alert for critical anomaly."""
        # TODO: Implement notification sending (Task 9)
        # For now, just mark as sent
        anomaly.alert_sent = True
        anomaly.alert_sent_at = timezone.now()
        anomaly.save()
        
        logger.warning(f"CRITICAL ANOMALY DETECTED: {anomaly.anomaly_type} on asset {anomaly.photo.asset.name}")
    
    # ========================================================================
    # METER READING EXTRACTION
    # ========================================================================
    
    def _extract_meter_readings(self, photo: InspectionPhoto,
                               result: ImageAnalysisResult,
                               analysis_data: Dict[str, Any]):
        """
        Extract meter readings from OCR text annotations.
        This is a basic implementation - will be enhanced in Task 5.
        """
        text_annotations = analysis_data.get('texts', [])
        
        if not text_annotations:
            return
        
        # Get the first annotation (full text)
        if len(text_annotations) > 0:
            full_text = text_annotations[0].get('description', '')
            
            # Try to extract numeric readings
            readings = self._extract_numeric_readings(full_text)
            
            for reading_value, confidence in readings:
                # Create meter reading
                # For now, we'll assume it's an odometer reading
                # This will be enhanced with ML classification in Task 5
                
                meter_reading = MeterReading.objects.create(
                    photo=photo,
                    asset=photo.asset,
                    reading_type=MeterReading.TYPE_ODOMETER,
                    value=reading_value,
                    unit='km',
                    confidence=confidence,
                    text_detected=full_text[:100],  # First 100 chars
                    bounding_box={'x': 0, 'y': 0, 'width': 1, 'height': 1},
                    is_valid=True,
                    is_outlier=False
                )
                
                # Check if reading is within expected range
                self._validate_meter_reading(meter_reading)
                
                logger.info(f"Created meter reading {meter_reading.id}: {reading_value} {meter_reading.unit}")
    
    def _extract_numeric_readings(self, text: str) -> list:
        """
        Extract numeric readings from text.
        Returns list of (value, confidence) tuples.
        """
        import re
        
        readings = []
        
        # Pattern to match numbers (with optional decimal point)
        pattern = r'\b\d+\.?\d*\b'
        matches = re.findall(pattern, text)
        
        for match in matches:
            try:
                value = float(match)
                # Only consider reasonable odometer values (0-999999)
                if 0 <= value <= 999999:
                    # Confidence based on OCR quality (simplified)
                    confidence = 0.85  # Default confidence
                    readings.append((value, confidence))
            except ValueError:
                continue
        
        return readings
    
    def _validate_meter_reading(self, reading: MeterReading):
        """
        Validate meter reading against historical data.
        Will be enhanced in Task 5.
        """
        # Get previous reading for this asset
        previous_readings = MeterReading.objects.filter(
            asset=reading.asset,
            reading_type=reading.reading_type,
            created_at__lt=reading.created_at
        ).order_by('-created_at')[:10]
        
        if previous_readings.exists():
            values = [r.value for r in previous_readings]
            avg = sum(values) / len(values)
            
            # Simple outlier detection (more than 50% deviation)
            if abs(reading.value - avg) > (avg * 0.5):
                reading.is_outlier = True
                reading.validation_notes = f"Value deviates significantly from average ({avg:.2f})"
                reading.save()
                
                logger.warning(f"Outlier detected: {reading.value} vs avg {avg:.2f}")
    
    # ========================================================================
    # CACHING
    # ========================================================================
    
    def _check_cache(self, image_url: str) -> Optional[ImageAnalysisResult]:
        """
        Check if we have cached results for this image URL.
        """
        try:
            # Look for recent analysis of the same image
            cached = ImageAnalysisResult.objects.filter(
                photo__original_url=image_url,
                cache_expires_at__gt=timezone.now()
            ).order_by('-created_at').first()
            
            return cached
            
        except Exception as e:
            logger.error(f"Error checking cache: {str(e)}")
            return None
    
    def _create_result_from_cache(self, photo: InspectionPhoto,
                                  cached: ImageAnalysisResult) -> ImageAnalysisResult:
        """Create new result from cached data."""
        
        result = ImageAnalysisResult.objects.create(
            photo=photo,
            labels=cached.labels,
            detected_objects=cached.detected_objects,
            text_annotations=cached.text_annotations,
            dominant_colors=cached.dominant_colors,
            safe_search=cached.safe_search,
            anomalies_detected=cached.anomalies_detected,
            anomaly_confidence=cached.anomaly_confidence,
            damage_type=cached.damage_type,
            damage_severity=cached.damage_severity,
            damage_confidence=cached.damage_confidence,
            processing_time_ms=0,  # Cached, no processing time
            model_version=cached.model_version,
            vision_ai_used=True,
            cached_result=True,
            cache_expires_at=cached.cache_expires_at
        )
        
        return result
    
    # ========================================================================
    # BATCH PROCESSING
    # ========================================================================
    
    def analyze_batch(self, photo_ids: list) -> Dict[str, Any]:
        """
        Analyze multiple photos in batch.
        
        Args:
            photo_ids: List of InspectionPhoto IDs
            
        Returns:
            Dict with success/failure counts and results
        """
        results = {
            'total': len(photo_ids),
            'success': 0,
            'failed': 0,
            'cached': 0,
            'results': []
        }
        
        for photo_id in photo_ids:
            try:
                photo = InspectionPhoto.objects.get(id=photo_id)
                result = self.analyze_inspection_photo(photo)
                
                results['success'] += 1
                if result.cached_result:
                    results['cached'] += 1
                
                results['results'].append({
                    'photo_id': str(photo_id),
                    'status': 'success',
                    'result_id': str(result.id)
                })
                
            except InspectionPhoto.DoesNotExist:
                results['failed'] += 1
                results['results'].append({
                    'photo_id': str(photo_id),
                    'status': 'failed',
                    'error': 'Photo not found'
                })
                
            except Exception as e:
                results['failed'] += 1
                results['results'].append({
                    'photo_id': str(photo_id),
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Batch analysis complete: {results['success']}/{results['total']} successful")
        
        return results


# Create singleton instance
image_analysis_service = ImageAnalysisService()
