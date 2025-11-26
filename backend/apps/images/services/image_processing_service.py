"""
Image processing service for compression, metadata extraction, and Cloud Storage upload.
"""
import io
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from PIL import Image
import piexif
from google.cloud import storage
from django.conf import settings

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """
    Service for processing images before upload and analysis.
    Handles compression, metadata extraction, and Cloud Storage upload.
    """
    
    def __init__(self):
        """Initialize image processing service."""
        self.storage_client = None
        self.bucket = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize Google Cloud Storage client."""
        try:
            if settings.GCP_STORAGE_BUCKET_NAME:
                self.storage_client = storage.Client()
                self.bucket = self.storage_client.bucket(settings.GCP_STORAGE_BUCKET_NAME)
                logger.info(f"Cloud Storage initialized: {settings.GCP_STORAGE_BUCKET_NAME}")
            else:
                logger.warning("GCP_STORAGE_BUCKET_NAME not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Cloud Storage is available."""
        return self.bucket is not None
    
    # ========================================================================
    # IMAGE VALIDATION
    # ========================================================================
    
    def validate_image(self, image_file) -> Tuple[bool, Optional[str]]:
        """
        Validate image file format and size.
        
        Args:
            image_file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            if image_file.size > settings.MAX_IMAGE_SIZE_BYTES:
                return False, f"Image size exceeds maximum of {settings.MAX_IMAGE_SIZE_MB}MB"
            
            # Check file extension
            file_ext = image_file.name.split('.')[-1].lower()
            if f'.{file_ext}' not in settings.ALLOWED_IMAGE_EXTENSIONS:
                return False, f"Invalid file format. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"
            
            # Try to open image with PIL
            try:
                img = Image.open(image_file)
                img.verify()
                
                # Check format
                if img.format not in settings.ALLOWED_IMAGE_FORMATS:
                    return False, f"Invalid image format. Allowed: {', '.join(settings.ALLOWED_IMAGE_FORMATS)}"
                
                # Reset file pointer after verify
                image_file.seek(0)
                
            except Exception as e:
                return False, f"Invalid or corrupted image file: {str(e)}"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    # ========================================================================
    # METADATA EXTRACTION
    # ========================================================================
    
    def extract_metadata(self, image_file) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image.
        
        Args:
            image_file: Uploaded file object
            
        Returns:
            Dict containing extracted metadata
        """
        metadata = {
            'captured_at': None,
            'gps_latitude': None,
            'gps_longitude': None,
            'gps_altitude': None,
            'compass_heading': None,
            'device_info': {},
            'width': None,
            'height': None,
            'format': None,
        }
        
        try:
            img = Image.open(image_file)
            
            # Basic image info
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['format'] = img.format
            
            # Extract EXIF data
            if hasattr(img, '_getexif') and img._getexif():
                exif_dict = piexif.load(img.info.get('exif', b''))
                
                # Extract datetime
                if piexif.ExifIFD.DateTimeOriginal in exif_dict.get('Exif', {}):
                    datetime_str = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode('utf-8')
                    try:
                        metadata['captured_at'] = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        pass
                
                # Extract GPS data
                gps_info = exif_dict.get('GPS', {})
                if gps_info:
                    metadata.update(self._extract_gps_data(gps_info))
                
                # Extract device info
                if '0th' in exif_dict:
                    zeroth_ifd = exif_dict['0th']
                    device_info = {}
                    
                    if piexif.ImageIFD.Make in zeroth_ifd:
                        device_info['make'] = zeroth_ifd[piexif.ImageIFD.Make].decode('utf-8')
                    
                    if piexif.ImageIFD.Model in zeroth_ifd:
                        device_info['model'] = zeroth_ifd[piexif.ImageIFD.Model].decode('utf-8')
                    
                    if piexif.ImageIFD.Software in zeroth_ifd:
                        device_info['software'] = zeroth_ifd[piexif.ImageIFD.Software].decode('utf-8')
                    
                    metadata['device_info'] = device_info
            
            # If no capture date in EXIF, use current time
            if not metadata['captured_at']:
                metadata['captured_at'] = datetime.now()
            
            # Reset file pointer
            image_file.seek(0)
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            # Set defaults
            metadata['captured_at'] = datetime.now()
        
        return metadata
    
    def _extract_gps_data(self, gps_info: Dict) -> Dict[str, Any]:
        """Extract GPS coordinates from EXIF GPS info."""
        gps_data = {}
        
        try:
            # Extract latitude
            if piexif.GPSIFD.GPSLatitude in gps_info and piexif.GPSIFD.GPSLatitudeRef in gps_info:
                lat = gps_info[piexif.GPSIFD.GPSLatitude]
                lat_ref = gps_info[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
                latitude = self._convert_to_degrees(lat)
                if lat_ref == 'S':
                    latitude = -latitude
                gps_data['gps_latitude'] = latitude
            
            # Extract longitude
            if piexif.GPSIFD.GPSLongitude in gps_info and piexif.GPSIFD.GPSLongitudeRef in gps_info:
                lon = gps_info[piexif.GPSIFD.GPSLongitude]
                lon_ref = gps_info[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')
                longitude = self._convert_to_degrees(lon)
                if lon_ref == 'W':
                    longitude = -longitude
                gps_data['gps_longitude'] = longitude
            
            # Extract altitude
            if piexif.GPSIFD.GPSAltitude in gps_info:
                altitude = gps_info[piexif.GPSIFD.GPSAltitude]
                gps_data['gps_altitude'] = float(altitude[0]) / float(altitude[1])
            
            # Extract compass heading
            if piexif.GPSIFD.GPSImgDirection in gps_info:
                direction = gps_info[piexif.GPSIFD.GPSImgDirection]
                gps_data['compass_heading'] = float(direction[0]) / float(direction[1])
        
        except Exception as e:
            logger.error(f"Error extracting GPS data: {str(e)}")
        
        return gps_data
    
    def _convert_to_degrees(self, value) -> float:
        """Convert GPS coordinates to degrees."""
        d = float(value[0][0]) / float(value[0][1])
        m = float(value[1][0]) / float(value[1][1])
        s = float(value[2][0]) / float(value[2][1])
        return d + (m / 60.0) + (s / 3600.0)
    
    # ========================================================================
    # IMAGE COMPRESSION
    # ========================================================================
    
    def compress_image(self, image_file, max_size_bytes: int = None) -> Tuple[io.BytesIO, int]:
        """
        Compress image to target size while maintaining quality.
        
        Args:
            image_file: Uploaded file object
            max_size_bytes: Maximum size in bytes (default from settings)
            
        Returns:
            Tuple of (compressed_image_buffer, final_size)
        """
        if max_size_bytes is None:
            max_size_bytes = settings.COMPRESSED_IMAGE_SIZE_BYTES
        
        try:
            img = Image.open(image_file)
            
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Start with high quality
            quality = 95
            output = io.BytesIO()
            
            # Iteratively reduce quality until size is acceptable
            while quality > 20:
                output.seek(0)
                output.truncate()
                
                img.save(output, format='JPEG', quality=quality, optimize=True)
                size = output.tell()
                
                if size <= max_size_bytes:
                    break
                
                quality -= 5
            
            # If still too large, resize image
            if size > max_size_bytes:
                scale_factor = (max_size_bytes / size) ** 0.5
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                output.seek(0)
                output.truncate()
                img.save(output, format='JPEG', quality=85, optimize=True)
                size = output.tell()
            
            output.seek(0)
            logger.info(f"Image compressed to {size} bytes (quality: {quality})")
            
            return output, size
            
        except Exception as e:
            logger.error(f"Error compressing image: {str(e)}")
            raise
    
    # ========================================================================
    # CLOUD STORAGE UPLOAD
    # ========================================================================
    
    def upload_to_storage(self, image_buffer: io.BytesIO, filename: str, 
                         content_type: str = 'image/jpeg') -> str:
        """
        Upload image to Google Cloud Storage.
        
        Args:
            image_buffer: Image data buffer
            filename: Destination filename
            content_type: MIME type
            
        Returns:
            Public URL of uploaded image
        """
        if not self.is_available():
            raise RuntimeError("Cloud Storage is not available")
        
        try:
            blob = self.bucket.blob(filename)
            blob.upload_from_file(image_buffer, content_type=content_type)
            
            # Make blob publicly readable (optional - adjust based on security requirements)
            # blob.make_public()
            
            # Return gs:// URL for Vision AI
            url = f"gs://{self.bucket.name}/{filename}"
            logger.info(f"Image uploaded to {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Error uploading to Cloud Storage: {str(e)}")
            raise
    
    def generate_filename(self, asset_id: str, user_id: str, extension: str = 'jpg') -> str:
        """
        Generate unique filename for uploaded image.
        
        Args:
            asset_id: Asset UUID
            user_id: User UUID
            extension: File extension
            
        Returns:
            Generated filename with path
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"inspections/{asset_id}/{timestamp}_{user_id}.{extension}"
        return filename
    
    def generate_thumbnail_filename(self, original_filename: str) -> str:
        """Generate thumbnail filename from original filename."""
        parts = original_filename.rsplit('.', 1)
        return f"{parts[0]}_thumb.{parts[1]}"
    
    # ========================================================================
    # THUMBNAIL GENERATION
    # ========================================================================
    
    def create_thumbnail(self, image_file, size: Tuple[int, int] = (300, 300)) -> io.BytesIO:
        """
        Create thumbnail from image.
        
        Args:
            image_file: Original image file
            size: Thumbnail size (width, height)
            
        Returns:
            Thumbnail image buffer
        """
        try:
            img = Image.open(image_file)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save to buffer
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            logger.info(f"Thumbnail created: {img.width}x{img.height}")
            
            return output
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            raise
    
    # ========================================================================
    # COMPLETE PROCESSING PIPELINE
    # ========================================================================
    
    def process_and_upload(self, image_file, asset_id: str, user_id: str) -> Dict[str, Any]:
        """
        Complete image processing pipeline: validate, extract metadata, compress, upload.
        
        Args:
            image_file: Uploaded file object
            asset_id: Asset UUID
            user_id: User UUID
            
        Returns:
            Dict containing URLs, metadata, and file info
        """
        # Validate image
        is_valid, error_msg = self.validate_image(image_file)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Extract metadata
        metadata = self.extract_metadata(image_file)
        
        # Compress image
        compressed_buffer, compressed_size = self.compress_image(image_file)
        
        # Generate filename
        filename = self.generate_filename(asset_id, user_id)
        
        # Upload original (compressed) image
        original_url = self.upload_to_storage(compressed_buffer, filename)
        
        # Create and upload thumbnail
        image_file.seek(0)
        thumbnail_buffer = self.create_thumbnail(image_file)
        thumbnail_filename = self.generate_thumbnail_filename(filename)
        thumbnail_url = self.upload_to_storage(thumbnail_buffer, thumbnail_filename)
        
        # Prepare result
        result = {
            'original_url': original_url,
            'thumbnail_url': thumbnail_url,
            'file_size': compressed_size,
            'width': metadata['width'],
            'height': metadata['height'],
            'format': metadata['format'],
            'captured_at': metadata['captured_at'],
            'gps_latitude': metadata.get('gps_latitude'),
            'gps_longitude': metadata.get('gps_longitude'),
            'gps_altitude': metadata.get('gps_altitude'),
            'compass_heading': metadata.get('compass_heading'),
            'device_info': metadata.get('device_info', {}),
        }
        
        logger.info(f"Image processing complete: {filename}")
        
        return result


# Create singleton instance
image_processing_service = ImageProcessingService()
