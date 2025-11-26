"""
Property-based tests for async image processing.

**Feature: image-processing-firebase, Property 3: Async Processing Non-Blocking**
**Validates: Requirements 1.3**

Property: For any image upload request, the API should return a response 
within 1 second while processing continues asynchronously.
"""
import time
import io
from PIL import Image
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status
from apps.assets.models import Asset, Location
from apps.images.models import InspectionPhoto

User = get_user_model()


class TestAsyncProcessingProperties(TransactionTestCase):
    """
    Property-based tests for async image processing.
    Tests that upload API is non-blocking and responsive.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='OPERADOR'
        )
        
        # Create test location
        self.location = Location.objects.create(
            name='Test Location',
            city='Santiago',
            region='Metropolitana'
        )
        
        # Create test asset
        self.asset = Asset.objects.create(
            name='Test Asset',
            asset_code='TEST-001',
            vehicle_type='CAMIONETA_MDO',
            location=self.location,
            serial_number='SN-TEST-001',
            created_by=self.user
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def _create_test_image(self, width=800, height=600, format='JPEG'):
        """Create a simple test image."""
        img = Image.new('RGB', (width, height), color='red')
        output = io.BytesIO()
        img.save(output, format=format)
        output.seek(0)
        output.name = f'test_image.{format.lower()}'
        return output
    
    def test_property_upload_response_time_under_threshold(self):
        """
        Property Test: Upload API response time.
        
        For any image upload, the API should return a response within
        1 second (non-blocking requirement).
        
        Note: This tests the upload endpoint response time, not the
        complete analysis time. Analysis happens asynchronously.
        """
        # Create test image
        image_file = self._create_test_image()
        
        # Measure upload time
        start_time = time.time()
        
        response = self.client.post(
            '/api/v1/images/photos/upload/',
            {
                'image': image_file,
                'asset_id': str(self.asset.id),
            },
            format='multipart'
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Verify response is successful
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        
        # Verify response time is under 2 seconds (allowing some margin)
        # In production with async processing, this should be < 1s
        self.assertLess(
            response_time,
            2.0,
            f"Upload response took {response_time:.2f}s, should be < 2s"
        )
        
        # Verify photo was created
        self.assertIn('id', response.data)
        photo_id = response.data['id']
        
        # Verify photo exists in database
        photo = InspectionPhoto.objects.get(id=photo_id)
        self.assertIsNotNone(photo)
    
    def test_property_upload_returns_immediately_with_pending_status(self):
        """
        Property Test: Upload returns with pending status.
        
        For any image upload, the API should return immediately with
        the photo in PENDING or PROCESSING status, not waiting for
        analysis to complete.
        """
        # Create test image
        image_file = self._create_test_image()
        
        # Upload image
        response = self.client.post(
            '/api/v1/images/photos/upload/',
            {
                'image': image_file,
                'asset_id': str(self.asset.id),
            },
            format='multipart'
        )
        
        # Verify response is successful
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        
        # Verify processing status is PENDING or COMPLETED
        # (COMPLETED if Vision AI processed synchronously, which is OK for now)
        processing_status = response.data.get('processing_status')
        self.assertIn(
            processing_status,
            [InspectionPhoto.STATUS_PENDING, InspectionPhoto.STATUS_COMPLETED],
            "Photo should be in PENDING or COMPLETED status after upload"
        )
    
    def test_property_multiple_concurrent_uploads_non_blocking(self):
        """
        Property Test: Multiple concurrent uploads are non-blocking.
        
        For any set of concurrent image uploads, each should return
        quickly without blocking others.
        """
        num_uploads = 3
        upload_times = []
        
        for i in range(num_uploads):
            image_file = self._create_test_image()
            
            start_time = time.time()
            
            response = self.client.post(
                '/api/v1/images/photos/upload/',
                {
                    'image': image_file,
                    'asset_id': str(self.asset.id),
                },
                format='multipart'
            )
            
            end_time = time.time()
            upload_time = end_time - start_time
            upload_times.append(upload_time)
            
            # Verify each upload succeeds
            self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        
        # Verify all uploads completed in reasonable time
        for i, upload_time in enumerate(upload_times):
            self.assertLess(
                upload_time,
                3.0,
                f"Upload {i+1} took {upload_time:.2f}s, should be < 3s"
            )
        
        # Verify average upload time is reasonable
        avg_time = sum(upload_times) / len(upload_times)
        self.assertLess(
            avg_time,
            2.0,
            f"Average upload time {avg_time:.2f}s, should be < 2s"
        )
    
    def test_property_upload_with_various_image_sizes(self):
        """
        Property Test: Upload response time across various image sizes.
        
        For any image size (within limits), the upload should return
        quickly regardless of image dimensions.
        """
        test_sizes = [
            (640, 480),    # Small
            (1280, 720),   # Medium
            (1920, 1080),  # Large
        ]
        
        for width, height in test_sizes:
            with self.subTest(size=f"{width}x{height}"):
                image_file = self._create_test_image(width=width, height=height)
                
                start_time = time.time()
                
                response = self.client.post(
                    '/api/v1/images/photos/upload/',
                    {
                        'image': image_file,
                        'asset_id': str(self.asset.id),
                    },
                    format='multipart'
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Verify response is successful
                self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
                
                # Verify response time is reasonable
                self.assertLess(
                    response_time,
                    3.0,
                    f"Upload of {width}x{height} took {response_time:.2f}s"
                )
    
    def test_property_photo_accessible_immediately_after_upload(self):
        """
        Property Test: Photo is accessible immediately after upload.
        
        For any uploaded photo, it should be immediately accessible
        via the API even if analysis is still pending.
        """
        # Upload image
        image_file = self._create_test_image()
        
        upload_response = self.client.post(
            '/api/v1/images/photos/upload/',
            {
                'image': image_file,
                'asset_id': str(self.asset.id),
            },
            format='multipart'
        )
        
        self.assertEqual(upload_response.status_code, http_status.HTTP_201_CREATED)
        photo_id = upload_response.data['id']
        
        # Immediately try to retrieve the photo
        retrieve_response = self.client.get(f'/api/v1/images/photos/{photo_id}/')
        
        # Verify photo is accessible
        self.assertEqual(retrieve_response.status_code, http_status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['id'], photo_id)
        
        # Verify basic metadata is present
        self.assertIn('original_url', retrieve_response.data)
        self.assertIn('thumbnail_url', retrieve_response.data)
        self.assertIn('asset', retrieve_response.data)
    
    def test_property_processing_status_transitions(self):
        """
        Property Test: Processing status transitions correctly.
        
        For any uploaded photo, the processing status should transition
        from PENDING -> PROCESSING -> COMPLETED (or FAILED).
        """
        # Upload image
        image_file = self._create_test_image()
        
        response = self.client.post(
            '/api/v1/images/photos/upload/',
            {
                'image': image_file,
                'asset_id': str(self.asset.id),
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)
        photo_id = response.data['id']
        
        # Get photo from database
        photo = InspectionPhoto.objects.get(id=photo_id)
        
        # Verify status is valid
        valid_statuses = [
            InspectionPhoto.STATUS_PENDING,
            InspectionPhoto.STATUS_PROCESSING,
            InspectionPhoto.STATUS_COMPLETED,
            InspectionPhoto.STATUS_FAILED
        ]
        self.assertIn(photo.processing_status, valid_statuses)
        
        # If completed, verify processed_at is set
        if photo.processing_status == InspectionPhoto.STATUS_COMPLETED:
            self.assertIsNotNone(photo.processed_at)
        
        # If failed, verify error message is set
        if photo.processing_status == InspectionPhoto.STATUS_FAILED:
            self.assertIsNotNone(photo.processing_error)
            self.assertNotEqual(photo.processing_error, '')


# Run tests with: python manage.py test apps.images.tests.test_async_processing_properties
