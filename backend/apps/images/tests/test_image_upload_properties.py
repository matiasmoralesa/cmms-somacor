"""
Property-based tests for image upload functionality.

**Feature: image-processing-firebase, Property 2: Metadata Extraction Completeness**
**Validates: Requirements 1.2**

Property: For any image with EXIF metadata, all required fields 
(timestamp, GPS, device info) should be extracted and stored.
"""
import io
import os
from datetime import datetime
from PIL import Image
import piexif
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.assets.models import Asset, Location
from apps.images.services.image_processing_service import ImageProcessingService
from apps.images.models import InspectionPhoto

User = get_user_model()


class TestImageUploadProperties(TestCase):
    """
    Property-based tests for image upload.
    Tests metadata extraction completeness across various image types.
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
        
        self.service = ImageProcessingService()
    
    def _create_test_image_with_exif(self, width=800, height=600, 
                                     include_gps=True, include_device=True):
        """
        Create a test image with EXIF metadata.
        
        Args:
            width: Image width
            height: Image height
            include_gps: Whether to include GPS data
            include_device: Whether to include device info
            
        Returns:
            BytesIO buffer containing image with EXIF
        """
        # Create image
        img = Image.new('RGB', (width, height), color='red')
        
        # Create EXIF data
        exif_dict = {
            '0th': {},
            'Exif': {},
            'GPS': {},
        }
        
        # Add datetime
        datetime_str = '2023:11:25 12:30:45'
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = datetime_str.encode('utf-8')
        
        # Add device info
        if include_device:
            exif_dict['0th'][piexif.ImageIFD.Make] = b'Apple'
            exif_dict['0th'][piexif.ImageIFD.Model] = b'iPhone 12'
            exif_dict['0th'][piexif.ImageIFD.Software] = b'iOS 15.0'
        
        # Add GPS data (Santiago, Chile coordinates)
        if include_gps:
            # Latitude: -33.4489 (33° 26' 56" S)
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = (
                (33, 1), (26, 1), (56, 1)
            )
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = b'S'
            
            # Longitude: -70.6693 (70° 40' 9" W)
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = (
                (70, 1), (40, 1), (9, 1)
            )
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = b'W'
            
            # Altitude: 570m
            exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (570, 1)
            
            # Compass heading: 45°
            exif_dict['GPS'][piexif.GPSIFD.GPSImgDirection] = (45, 1)
        
        # Convert to bytes
        exif_bytes = piexif.dump(exif_dict)
        
        # Save image with EXIF
        output = io.BytesIO()
        img.save(output, format='JPEG', exif=exif_bytes)
        output.seek(0)
        output.name = 'test_image.jpg'
        
        return output
    
    def test_property_metadata_extraction_with_full_exif(self):
        """
        Property Test: Metadata extraction completeness with full EXIF data.
        
        For any image with complete EXIF metadata (GPS, device, datetime),
        all required fields should be extracted and stored correctly.
        """
        # Generate test image with full EXIF
        image_file = self._create_test_image_with_exif(
            width=1920,
            height=1080,
            include_gps=True,
            include_device=True
        )
        
        # Extract metadata
        metadata = self.service.extract_metadata(image_file)
        
        # Verify all required fields are present
        self.assertIsNotNone(metadata['captured_at'], "Capture datetime should be extracted")
        self.assertIsNotNone(metadata['gps_latitude'], "GPS latitude should be extracted")
        self.assertIsNotNone(metadata['gps_longitude'], "GPS longitude should be extracted")
        self.assertIsNotNone(metadata['gps_altitude'], "GPS altitude should be extracted")
        self.assertIsNotNone(metadata['compass_heading'], "Compass heading should be extracted")
        self.assertIsNotNone(metadata['device_info'], "Device info should be extracted")
        
        # Verify GPS coordinates are correct (Santiago, Chile)
        self.assertAlmostEqual(float(metadata['gps_latitude']), -33.4489, places=2)
        self.assertAlmostEqual(float(metadata['gps_longitude']), -70.6693, places=2)
        
        # Verify device info contains expected fields
        self.assertIn('make', metadata['device_info'])
        self.assertIn('model', metadata['device_info'])
        self.assertEqual(metadata['device_info']['make'], 'Apple')
        self.assertEqual(metadata['device_info']['model'], 'iPhone 12')
    
    def test_property_metadata_extraction_without_gps(self):
        """
        Property Test: Metadata extraction with missing GPS data.
        
        For any image without GPS data, the system should still extract
        other metadata and handle missing GPS gracefully.
        """
        # Generate test image without GPS
        image_file = self._create_test_image_with_exif(
            include_gps=False,
            include_device=True
        )
        
        # Extract metadata
        metadata = self.service.extract_metadata(image_file)
        
        # Verify datetime and device info are still extracted
        self.assertIsNotNone(metadata['captured_at'])
        self.assertIsNotNone(metadata['device_info'])
        
        # Verify GPS fields are None
        self.assertIsNone(metadata['gps_latitude'])
        self.assertIsNone(metadata['gps_longitude'])
        self.assertIsNone(metadata['gps_altitude'])
        self.assertIsNone(metadata['compass_heading'])
    
    def test_property_metadata_extraction_without_device_info(self):
        """
        Property Test: Metadata extraction with missing device info.
        
        For any image without device info, the system should still extract
        GPS and datetime metadata.
        """
        # Generate test image without device info
        image_file = self._create_test_image_with_exif(
            include_gps=True,
            include_device=False
        )
        
        # Extract metadata
        metadata = self.service.extract_metadata(image_file)
        
        # Verify GPS and datetime are extracted
        self.assertIsNotNone(metadata['captured_at'])
        self.assertIsNotNone(metadata['gps_latitude'])
        self.assertIsNotNone(metadata['gps_longitude'])
        
        # Verify device info is empty dict
        self.assertEqual(metadata['device_info'], {})
    
    def test_property_metadata_extraction_various_image_sizes(self):
        """
        Property Test: Metadata extraction across various image sizes.
        
        For any image size, metadata extraction should work correctly
        and return consistent results.
        """
        test_sizes = [
            (640, 480),    # VGA
            (1280, 720),   # HD
            (1920, 1080),  # Full HD
            (3840, 2160),  # 4K
        ]
        
        for width, height in test_sizes:
            with self.subTest(size=f"{width}x{height}"):
                image_file = self._create_test_image_with_exif(
                    width=width,
                    height=height,
                    include_gps=True,
                    include_device=True
                )
                
                metadata = self.service.extract_metadata(image_file)
                
                # Verify dimensions are correct
                self.assertEqual(metadata['width'], width)
                self.assertEqual(metadata['height'], height)
                
                # Verify metadata is extracted regardless of size
                self.assertIsNotNone(metadata['captured_at'])
                self.assertIsNotNone(metadata['gps_latitude'])
                self.assertIsNotNone(metadata['device_info'])
    
    def test_property_metadata_persistence_in_database(self):
        """
        Property Test: Metadata persistence in database.
        
        For any uploaded image, all extracted metadata should be
        correctly stored in the database and retrievable.
        """
        # Create test image
        image_file = self._create_test_image_with_exif(
            include_gps=True,
            include_device=True
        )
        
        # Extract metadata
        metadata = self.service.extract_metadata(image_file)
        
        # Create InspectionPhoto record
        photo = InspectionPhoto.objects.create(
            asset=self.asset,
            original_url='gs://test-bucket/test.jpg',
            thumbnail_url='gs://test-bucket/test_thumb.jpg',
            file_size=100000,
            width=metadata['width'],
            height=metadata['height'],
            format=metadata['format'],
            captured_at=metadata['captured_at'],
            gps_latitude=metadata.get('gps_latitude'),
            gps_longitude=metadata.get('gps_longitude'),
            gps_altitude=metadata.get('gps_altitude'),
            compass_heading=metadata.get('compass_heading'),
            device_info=metadata.get('device_info', {}),
            uploaded_by=self.user
        )
        
        # Retrieve from database
        retrieved_photo = InspectionPhoto.objects.get(id=photo.id)
        
        # Verify all metadata is persisted
        self.assertEqual(retrieved_photo.width, metadata['width'])
        self.assertEqual(retrieved_photo.height, metadata['height'])
        self.assertEqual(retrieved_photo.format, metadata['format'])
        self.assertIsNotNone(retrieved_photo.captured_at)
        self.assertIsNotNone(retrieved_photo.gps_latitude)
        self.assertIsNotNone(retrieved_photo.gps_longitude)
        self.assertIsNotNone(retrieved_photo.device_info)
        
        # Verify GPS coordinates match
        self.assertAlmostEqual(
            float(retrieved_photo.gps_latitude),
            float(metadata['gps_latitude']),
            places=4
        )
        self.assertAlmostEqual(
            float(retrieved_photo.gps_longitude),
            float(metadata['gps_longitude']),
            places=4
        )
    
    def test_property_default_datetime_when_missing(self):
        """
        Property Test: Default datetime when EXIF datetime is missing.
        
        For any image without EXIF datetime, the system should use
        current datetime as fallback.
        """
        # Create image without EXIF
        img = Image.new('RGB', (800, 600), color='blue')
        output = io.BytesIO()
        img.save(output, format='JPEG')
        output.seek(0)
        output.name = 'test_no_exif.jpg'
        
        # Extract metadata
        before_extraction = datetime.now()
        metadata = self.service.extract_metadata(output)
        after_extraction = datetime.now()
        
        # Verify datetime is set to current time
        self.assertIsNotNone(metadata['captured_at'])
        self.assertGreaterEqual(metadata['captured_at'], before_extraction)
        self.assertLessEqual(metadata['captured_at'], after_extraction)


# Run tests with: python manage.py test apps.images.tests.test_image_upload_properties
