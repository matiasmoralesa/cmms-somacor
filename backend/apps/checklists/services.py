"""Services for checklist operations"""
from django.core.files.base import ContentFile
from utils.gcp_storage import storage_client
from .pdf_generator import ChecklistPDFGenerator
import logging

logger = logging.getLogger(__name__)


class ChecklistService:
    """Service for checklist business logic"""
    
    @staticmethod
    def generate_and_upload_pdf(checklist_response):
        """
        Generate PDF for checklist response and upload to Cloud Storage
        
        This method is designed to be fault-tolerant. If PDF generation fails,
        it logs the error but doesn't raise an exception, allowing the checklist
        to be saved without a PDF.
        
        Args:
            checklist_response: ChecklistResponse instance
            
        Returns:
            str: GCS URL of uploaded PDF, or None if generation failed
        """
        try:
            # Generate PDF
            logger.info(f"Starting PDF generation for checklist {checklist_response.id}")
            pdf_generator = ChecklistPDFGenerator(checklist_response)
            pdf_buffer = pdf_generator.generate()
            
            # Create filename
            filename = (
                f"checklist_{checklist_response.template.code}_"
                f"{checklist_response.asset.asset_code}_"
                f"{checklist_response.completed_at.strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            # Upload to Cloud Storage
            if storage_client:
                pdf_file = ContentFile(pdf_buffer.read(), name=filename)
                pdf_url, _, _ = storage_client.upload_file(
                    pdf_file,
                    folder='checklists',
                    filename=filename
                )
                
                # Update checklist with PDF URL
                checklist_response.pdf_url = pdf_url
                checklist_response.save(update_fields=['pdf_url'])
                
                logger.info(f"PDF generated and uploaded successfully for checklist {checklist_response.id}")
                return pdf_url
            else:
                logger.warning("GCP Storage client not configured - PDF generation skipped")
                return None
                
        except ImportError as e:
            logger.warning(
                f"PDF generation dependencies not available for checklist {checklist_response.id}: {e}. "
                "Install LibreOffice or required libraries to enable PDF generation."
            )
            return None
        except Exception as e:
            logger.error(
                f"Error generating PDF for checklist {checklist_response.id}: {e}. "
                "Checklist saved without PDF. You can regenerate the PDF later.",
                exc_info=True
            )
            return None
    
    @staticmethod
    def get_pdf_signed_url(checklist_response, expiration=3600):
        """
        Get signed URL for checklist PDF
        
        Args:
            checklist_response: ChecklistResponse instance
            expiration: URL expiration in seconds (default 1 hour)
            
        Returns:
            str: Signed URL for PDF access
        """
        if not checklist_response.pdf_url:
            return None
        
        if storage_client:
            try:
                signed_url = storage_client.get_signed_url(
                    checklist_response.pdf_url,
                    expiration=expiration
                )
                return signed_url
            except Exception as e:
                logger.error(f"Error generating signed URL for checklist {checklist_response.id}: {e}")
                return None
        
        return checklist_response.pdf_url
    
    @staticmethod
    def validate_checklist_for_asset(template, asset):
        """
        Validate that checklist template matches asset vehicle type
        
        Args:
            template: ChecklistTemplate instance
            asset: Asset instance
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if template.vehicle_type != asset.vehicle_type:
            return False, (
                f"Esta plantilla es para {template.vehicle_type}, "
                f"pero el activo es {asset.vehicle_type}"
            )
        
        return True, None
