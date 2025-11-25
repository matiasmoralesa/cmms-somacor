"""
Vertex AI Client for ML model deployment and predictions
"""
import os
import json
from typing import Dict, List, Optional
from django.conf import settings


class VertexAIClient:
    """
    Client for interacting with Google Cloud Vertex AI
    Supports both local development and production deployment
    """
    
    def __init__(self):
        self.project_id = getattr(settings, 'GCP_PROJECT_ID', None)
        self.location = getattr(settings, 'GCP_LOCATION', 'us-central1')
        self.endpoint_id = getattr(settings, 'VERTEX_AI_ENDPOINT_ID', None)
        self.use_vertex_ai = getattr(settings, 'USE_VERTEX_AI', False)
        
        # Initialize Vertex AI client if in production
        if self.use_vertex_ai and self.project_id:
            try:
                from google.cloud import aiplatform
                aiplatform.init(project=self.project_id, location=self.location)
                self.aiplatform = aiplatform
                self.client_initialized = True
            except ImportError:
                print("Warning: google-cloud-aiplatform not installed. Using local model.")
                self.client_initialized = False
        else:
            self.client_initialized = False
    
    def deploy_model(self, model_path: str, model_display_name: str) -> Optional[str]:
        """
        Deploy a trained model to Vertex AI
        
        Args:
            model_path: Path to the saved model file
            model_display_name: Display name for the model in Vertex AI
            
        Returns:
            Endpoint ID if successful, None otherwise
        """
        if not self.client_initialized:
            print("Vertex AI not configured. Skipping deployment.")
            return None
        
        try:
            # Upload model to Vertex AI
            model = self.aiplatform.Model.upload(
                display_name=model_display_name,
                artifact_uri=model_path,
                serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
            )
            
            # Create endpoint
            endpoint = self.aiplatform.Endpoint.create(
                display_name=f"{model_display_name}-endpoint"
            )
            
            # Deploy model to endpoint
            endpoint.deploy(
                model=model,
                deployed_model_display_name=model_display_name,
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=3,
            )
            
            return endpoint.resource_name
            
        except Exception as e:
            print(f"Error deploying model to Vertex AI: {e}")
            return None
    
    def predict(self, instances: List[List[float]]) -> Dict:
        """
        Make predictions using Vertex AI endpoint
        
        Args:
            instances: List of feature vectors for prediction
            
        Returns:
            Dictionary with predictions and metadata
        """
        if not self.client_initialized or not self.endpoint_id:
            # Fallback to local model
            return self._local_predict(instances)
        
        try:
            endpoint = self.aiplatform.Endpoint(self.endpoint_id)
            predictions = endpoint.predict(instances=instances)
            
            return {
                'predictions': predictions.predictions,
                'deployed_model_id': predictions.deployed_model_id,
                'model_version_id': predictions.model_version_id,
                'source': 'vertex_ai'
            }
            
        except Exception as e:
            print(f"Error calling Vertex AI endpoint: {e}")
            # Fallback to local model
            return self._local_predict(instances)
    
    def _local_predict(self, instances: List[List[float]]) -> Dict:
        """
        Fallback to local model prediction
        
        Args:
            instances: List of feature vectors for prediction
            
        Returns:
            Dictionary with predictions
        """
        from .ml_service import MLPredictionService
        
        ml_service = MLPredictionService()
        
        # Load local model
        if not ml_service.load_model():
            ml_service.train_model()
        
        # Make predictions
        import numpy as np
        predictions = []
        
        for instance in instances:
            try:
                proba = ml_service.model.predict_proba([instance])[0]
                predictions.append({
                    'failure_probability': float(proba[1] * 100),
                    'confidence': float(max(proba))
                })
            except Exception as e:
                print(f"Error in local prediction: {e}")
                predictions.append({
                    'failure_probability': 0.0,
                    'confidence': 0.0
                })
        
        return {
            'predictions': predictions,
            'source': 'local_model'
        }
    
    def get_model_info(self) -> Dict:
        """
        Get information about the deployed model
        
        Returns:
            Dictionary with model information
        """
        if not self.client_initialized or not self.endpoint_id:
            return {
                'status': 'local',
                'message': 'Using local model',
                'vertex_ai_enabled': False
            }
        
        try:
            endpoint = self.aiplatform.Endpoint(self.endpoint_id)
            
            return {
                'status': 'deployed',
                'endpoint_id': self.endpoint_id,
                'display_name': endpoint.display_name,
                'deployed_models': len(endpoint.list_models()),
                'vertex_ai_enabled': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'vertex_ai_enabled': True
            }
    
    def batch_predict(self, 
                     input_data: List[Dict],
                     output_uri: str) -> Optional[str]:
        """
        Run batch prediction job on Vertex AI
        
        Args:
            input_data: List of input data dictionaries
            output_uri: GCS URI for output results
            
        Returns:
            Job ID if successful, None otherwise
        """
        if not self.client_initialized:
            print("Vertex AI not configured. Cannot run batch prediction.")
            return None
        
        try:
            # Create batch prediction job
            job = self.aiplatform.BatchPredictionJob.create(
                job_display_name="cmms-failure-prediction-batch",
                model_name=self.endpoint_id,
                instances_format="jsonl",
                predictions_format="jsonl",
                gcs_source=input_data,
                gcs_destination_prefix=output_uri,
                machine_type="n1-standard-2",
            )
            
            return job.resource_name
            
        except Exception as e:
            print(f"Error creating batch prediction job: {e}")
            return None
    
    def list_models(self) -> List[Dict]:
        """
        List all models in Vertex AI
        
        Returns:
            List of model information dictionaries
        """
        if not self.client_initialized:
            return []
        
        try:
            models = self.aiplatform.Model.list()
            
            return [
                {
                    'name': model.display_name,
                    'resource_name': model.resource_name,
                    'create_time': str(model.create_time),
                    'update_time': str(model.update_time),
                }
                for model in models
            ]
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """
        Delete a Vertex AI endpoint
        
        Args:
            endpoint_id: ID of the endpoint to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client_initialized:
            return False
        
        try:
            endpoint = self.aiplatform.Endpoint(endpoint_id)
            endpoint.delete(force=True)
            return True
            
        except Exception as e:
            print(f"Error deleting endpoint: {e}")
            return False


# Singleton instance
_vertex_ai_client = None


def get_vertex_ai_client() -> VertexAIClient:
    """
    Get or create the Vertex AI client singleton
    
    Returns:
        VertexAIClient instance
    """
    global _vertex_ai_client
    if _vertex_ai_client is None:
        _vertex_ai_client = VertexAIClient()
    return _vertex_ai_client
