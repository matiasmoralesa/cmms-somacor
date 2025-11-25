"""Google Cloud Storage utility"""
from google.cloud import storage
from django.conf import settings
import uuid
import os


class GCPStorageClient:
    """Client for Google Cloud Storage operations"""
    
    def __init__(self):
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket_name = settings.GCP_STORAGE_BUCKET_NAME
        self.bucket = self.client.bucket(self.bucket_name)
    
    def upload_file(self, file, folder='documents', filename=None):
        """
        Upload file to GCS
        
        Args:
            file: File object
            folder: Folder path in bucket
            filename: Custom filename (optional)
        
        Returns:
            tuple: (file_url, file_name, file_size)
        """
        if not filename:
            # Generate unique filename
            ext = os.path.splitext(file.name)[1]
            filename = f"{uuid.uuid4()}{ext}"
        
        blob_name = f"{folder}/{filename}"
        blob = self.bucket.blob(blob_name)
        
        # Upload file
        blob.upload_from_file(file, content_type=file.content_type if hasattr(file, 'content_type') else None)
        
        # Make public (optional - configure based on requirements)
        # blob.make_public()
        
        file_url = f"gs://{self.bucket_name}/{blob_name}"
        file_size = blob.size
        
        return file_url, filename, file_size
    
    def delete_file(self, file_url):
        """
        Delete file from GCS
        
        Args:
            file_url: GCS URL (gs://bucket/path)
        """
        # Extract blob name from URL
        blob_name = file_url.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(blob_name)
        blob.delete()
    
    def get_signed_url(self, file_url, expiration=3600):
        """
        Get signed URL for private file access
        
        Args:
            file_url: GCS URL
            expiration: URL expiration in seconds
        
        Returns:
            str: Signed URL
        """
        blob_name = file_url.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(blob_name)
        
        url = blob.generate_signed_url(expiration=expiration)
        return url


# Singleton instance
storage_client = GCPStorageClient() if (settings.GCP_PROJECT_ID and settings.GCP_STORAGE_BUCKET_NAME) else None
