"""
Google Cloud Vision AI client for image analysis.
"""
import logging
from typing import List, Dict, Any, Optional
from google.cloud import vision
from google.cloud.vision_v1 import types
from django.conf import settings

logger = logging.getLogger(__name__)


class VisionAIClient:
    """
    Client for Google Cloud Vision AI API.
    Provides methods for label detection, OCR, object localization, and more.
    """
    
    def __init__(self):
        """Initialize Vision AI client."""
        self.client = vision.ImageAnnotatorClient()
        self.enabled = settings.VISION_AI_ENABLED
        self.max_results = settings.VISION_AI_MAX_RESULTS
    
    def is_available(self) -> bool:
        """Check if Vision AI is enabled and available."""
        return self.enabled
    
    def _create_image_from_url(self, image_url: str) -> types.Image:
        """Create Vision AI Image object from URL."""
        image = types.Image()
        image.source.image_uri = image_url
        return image
    
    def _create_image_from_content(self, image_content: bytes) -> types.Image:
        """Create Vision AI Image object from binary content."""
        return types.Image(content=image_content)
    
    # ========================================================================
    # LABEL DETECTION
    # ========================================================================
    
    def detect_labels(self, image_url: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Detect labels (objects, concepts) in an image.
        
        Args:
            image_url: URL of the image to analyze
            max_results: Maximum number of labels to return
            
        Returns:
            List of detected labels with descriptions and confidence scores
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return []
        
        try:
            image = self._create_image_from_url(image_url)
            max_results = max_results or self.max_results
            
            response = self.client.label_detection(
                image=image,
                max_results=max_results
            )
            
            labels = []
            for label in response.label_annotations:
                labels.append({
                    'description': label.description,
                    'score': label.score,
                    'topicality': label.topicality,
                })
            
            logger.info(f"Detected {len(labels)} labels in image")
            return labels
            
        except Exception as e:
            logger.error(f"Failed to detect labels: {str(e)}")
            raise
    
    # ========================================================================
    # TEXT DETECTION (OCR)
    # ========================================================================
    
    def detect_text(self, image_url: str) -> List[Dict[str, Any]]:
        """
        Detect and extract text from an image using OCR.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            List of detected text annotations with content and bounding boxes
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return []
        
        try:
            image = self._create_image_from_url(image_url)
            
            response = self.client.text_detection(image=image)
            
            texts = []
            for text in response.text_annotations:
                # Get bounding box vertices
                vertices = []
                for vertex in text.bounding_poly.vertices:
                    vertices.append({
                        'x': vertex.x,
                        'y': vertex.y,
                    })
                
                texts.append({
                    'description': text.description,
                    'locale': text.locale if hasattr(text, 'locale') else None,
                    'bounding_box': vertices,
                })
            
            logger.info(f"Detected {len(texts)} text annotations in image")
            return texts
            
        except Exception as e:
            logger.error(f"Failed to detect text: {str(e)}")
            raise
    
    def detect_document_text(self, image_url: str) -> Dict[str, Any]:
        """
        Detect and extract document text with detailed structure.
        Better for dense text and documents.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict containing full text and detailed page/block/paragraph structure
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return {}
        
        try:
            image = self._create_image_from_url(image_url)
            
            response = self.client.document_text_detection(image=image)
            
            if not response.full_text_annotation:
                return {'text': '', 'pages': []}
            
            result = {
                'text': response.full_text_annotation.text,
                'pages': [],
            }
            
            for page in response.full_text_annotation.pages:
                page_data = {
                    'width': page.width,
                    'height': page.height,
                    'blocks': [],
                }
                
                for block in page.blocks:
                    block_data = {
                        'paragraphs': [],
                        'confidence': block.confidence,
                    }
                    
                    for paragraph in block.paragraphs:
                        words = []
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            words.append({
                                'text': word_text,
                                'confidence': word.confidence,
                            })
                        
                        block_data['paragraphs'].append({
                            'words': words,
                            'confidence': paragraph.confidence,
                        })
                    
                    page_data['blocks'].append(block_data)
                
                result['pages'].append(page_data)
            
            logger.info(f"Detected document text with {len(result['pages'])} pages")
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect document text: {str(e)}")
            raise
    
    # ========================================================================
    # OBJECT LOCALIZATION
    # ========================================================================
    
    def detect_objects(self, image_url: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Detect and localize objects in an image with bounding boxes.
        
        Args:
            image_url: URL of the image to analyze
            max_results: Maximum number of objects to return
            
        Returns:
            List of detected objects with names, confidence, and bounding boxes
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return []
        
        try:
            image = self._create_image_from_url(image_url)
            max_results = max_results or self.max_results
            
            response = self.client.object_localization(
                image=image,
                max_results=max_results
            )
            
            objects = []
            for obj in response.localized_object_annotations:
                # Get normalized bounding box
                vertices = []
                for vertex in obj.bounding_poly.normalized_vertices:
                    vertices.append({
                        'x': vertex.x,
                        'y': vertex.y,
                    })
                
                objects.append({
                    'name': obj.name,
                    'score': obj.score,
                    'bounding_box': vertices,
                })
            
            logger.info(f"Detected {len(objects)} objects in image")
            return objects
            
        except Exception as e:
            logger.error(f"Failed to detect objects: {str(e)}")
            raise
    
    # ========================================================================
    # IMAGE PROPERTIES
    # ========================================================================
    
    def analyze_image_properties(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze image properties including dominant colors.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict containing dominant colors and other image properties
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return {}
        
        try:
            image = self._create_image_from_url(image_url)
            
            response = self.client.image_properties(image=image)
            
            properties = response.image_properties_annotation
            
            # Extract dominant colors
            colors = []
            for color in properties.dominant_colors.colors:
                colors.append({
                    'red': color.color.red,
                    'green': color.color.green,
                    'blue': color.color.blue,
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction,
                })
            
            result = {
                'dominant_colors': colors,
            }
            
            logger.info(f"Analyzed image properties with {len(colors)} dominant colors")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze image properties: {str(e)}")
            raise
    
    # ========================================================================
    # SAFE SEARCH DETECTION
    # ========================================================================
    
    def detect_safe_search(self, image_url: str) -> Dict[str, str]:
        """
        Detect potentially unsafe or inappropriate content.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict with likelihood ratings for adult, violence, racy, etc.
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return {}
        
        try:
            image = self._create_image_from_url(image_url)
            
            response = self.client.safe_search_detection(image=image)
            
            safe = response.safe_search_annotation
            
            # Convert likelihood enum to string
            likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                             'LIKELY', 'VERY_LIKELY')
            
            result = {
                'adult': likelihood_name[safe.adult],
                'violence': likelihood_name[safe.violence],
                'racy': likelihood_name[safe.racy],
                'spoof': likelihood_name[safe.spoof],
                'medical': likelihood_name[safe.medical],
            }
            
            logger.info("Performed safe search detection")
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect safe search: {str(e)}")
            raise
    
    # ========================================================================
    # COMPREHENSIVE ANALYSIS
    # ========================================================================
    
    def analyze_image_comprehensive(self, image_url: str) -> Dict[str, Any]:
        """
        Perform comprehensive image analysis including labels, text, objects, and properties.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Dict containing all analysis results
        """
        if not self.is_available():
            logger.warning("Vision AI is disabled")
            return {}
        
        try:
            image = self._create_image_from_url(image_url)
            
            # Perform multiple feature detections in one request
            features = [
                types.Feature(type_=types.Feature.Type.LABEL_DETECTION, max_results=self.max_results),
                types.Feature(type_=types.Feature.Type.TEXT_DETECTION),
                types.Feature(type_=types.Feature.Type.OBJECT_LOCALIZATION, max_results=self.max_results),
                types.Feature(type_=types.Feature.Type.IMAGE_PROPERTIES),
                types.Feature(type_=types.Feature.Type.SAFE_SEARCH_DETECTION),
            ]
            
            request = types.AnnotateImageRequest(image=image, features=features)
            response = self.client.annotate_image(request=request)
            
            # Process labels
            labels = [
                {
                    'description': label.description,
                    'score': label.score,
                    'topicality': label.topicality,
                }
                for label in response.label_annotations
            ]
            
            # Process text
            texts = [
                {
                    'description': text.description,
                    'bounding_box': [{'x': v.x, 'y': v.y} for v in text.bounding_poly.vertices],
                }
                for text in response.text_annotations
            ]
            
            # Process objects
            objects = [
                {
                    'name': obj.name,
                    'score': obj.score,
                    'bounding_box': [{'x': v.x, 'y': v.y} for v in obj.bounding_poly.normalized_vertices],
                }
                for obj in response.localized_object_annotations
            ]
            
            # Process colors
            colors = [
                {
                    'red': color.color.red,
                    'green': color.color.green,
                    'blue': color.color.blue,
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction,
                }
                for color in response.image_properties_annotation.dominant_colors.colors
            ]
            
            # Process safe search
            safe = response.safe_search_annotation
            likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                             'LIKELY', 'VERY_LIKELY')
            safe_search = {
                'adult': likelihood_name[safe.adult],
                'violence': likelihood_name[safe.violence],
                'racy': likelihood_name[safe.racy],
            }
            
            result = {
                'labels': labels,
                'texts': texts,
                'objects': objects,
                'dominant_colors': colors,
                'safe_search': safe_search,
            }
            
            logger.info("Completed comprehensive image analysis")
            return result
            
        except Exception as e:
            logger.error(f"Failed to perform comprehensive analysis: {str(e)}")
            raise


# Create singleton instance
vision_ai_client = VisionAIClient()
