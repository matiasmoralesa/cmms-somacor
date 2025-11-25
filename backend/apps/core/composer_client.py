"""
Cloud Composer (Airflow) Client for triggering DAGs
"""
import os
import logging
from typing import Optional, Dict, Any
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class ComposerClient:
    """Client for interacting with Cloud Composer / Airflow API"""
    
    def __init__(self):
        self.airflow_url = os.getenv('AIRFLOW_WEBSERVER_URL', '')
        self.airflow_username = os.getenv('AIRFLOW_USERNAME', 'admin')
        self.airflow_password = os.getenv('AIRFLOW_PASSWORD', '')
        self.client_initialized = bool(self.airflow_url and self.airflow_password)
        
        if not self.client_initialized:
            logger.warning("Cloud Composer client not initialized. Set AIRFLOW_WEBSERVER_URL and AIRFLOW_PASSWORD.")
    
    def trigger_dag(self, dag_id: str, conf: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        """
        Trigger a DAG run
        
        Args:
            dag_id: The ID of the DAG to trigger
            conf: Optional configuration dictionary to pass to the DAG
            
        Returns:
            Dict with DAG run information or None if failed
        """
        if not self.client_initialized:
            logger.error("Composer client not initialized")
            return None
        
        url = f"{self.airflow_url}/api/v1/dags/{dag_id}/dagRuns"
        
        payload = {
            "conf": conf or {}
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"DAG {dag_id} triggered successfully: {result.get('dag_run_id')}")
            
            return result
        except Exception as e:
            logger.error(f"Error triggering DAG {dag_id}: {str(e)}")
            return None

    def get_dag_status(self, dag_id: str) -> Optional[Dict]:
        """
        Get the status of a DAG
        
        Args:
            dag_id: The ID of the DAG
            
        Returns:
            Dict with DAG information or None if failed
        """
        if not self.client_initialized:
            logger.error("Composer client not initialized")
            return None
        
        url = f"{self.airflow_url}/api/v1/dags/{dag_id}"
        
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting DAG {dag_id} status: {str(e)}")
            return None
    
    def get_dag_runs(self, dag_id: str, limit: int = 10) -> Optional[list]:
        """
        Get recent DAG runs
        
        Args:
            dag_id: The ID of the DAG
            limit: Maximum number of runs to return
            
        Returns:
            List of DAG runs or None if failed
        """
        if not self.client_initialized:
            logger.error("Composer client not initialized")
            return None
        
        url = f"{self.airflow_url}/api/v1/dags/{dag_id}/dagRuns"
        params = {"limit": limit, "order_by": "-execution_date"}
        
        try:
            response = requests.get(
                url,
                params=params,
                auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('dag_runs', [])
        except Exception as e:
            logger.error(f"Error getting DAG {dag_id} runs: {str(e)}")
            return None
    
    def list_dags(self) -> Optional[list]:
        """
        List all available DAGs
        
        Returns:
            List of DAGs or None if failed
        """
        if not self.client_initialized:
            logger.error("Composer client not initialized")
            return None
        
        url = f"{self.airflow_url}/api/v1/dags"
        
        try:
            response = requests.get(
                url,
                auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('dags', [])
        except Exception as e:
            logger.error(f"Error listing DAGs: {str(e)}")
            return None


# Singleton instance
_composer_client = None

def get_composer_client() -> ComposerClient:
    """Get or create ComposerClient singleton instance"""
    global _composer_client
    if _composer_client is None:
        _composer_client = ComposerClient()
    return _composer_client
