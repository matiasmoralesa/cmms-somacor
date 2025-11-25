"""
ETL and ML Training DAG for CMMS System
Extracts data from Cloud SQL, performs feature engineering, trains ML model
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator
from airflow.utils.email import send_email
from airflow.models import Variable
import logging

# Configuration
PROJECT_ID = Variable.get("gcp_project_id", default_var="your-project-id")
REGION = Variable.get("gcp_region", default_var="us-central1")
CLUSTER_NAME = "cmms-ml-cluster"
BUCKET_NAME = Variable.get("gcs_bucket_name", default_var="cmms-ml-data")

# Default arguments
default_args = {
    'owner': 'cmms-admin',
    'depends_on_past': False,
    'email': Variable.get("alert_email", default_var="admin@cmms.com").split(','),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'etl_ml_training',
    default_args=default_args,
    description='ETL and ML model training pipeline',
    schedule_interval='0 2 * * 0',  # Weekly on Sunday at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ml', 'etl', 'training'],
)

# Dataproc cluster configuration
CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-4",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 100},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-4",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 100},
    },
}

# Task 1: Extract data from Cloud SQL to GCS
extract_assets_data = PostgresToGCSOperator(
    task_id='extract_assets_data',
    postgres_conn_id='cloudsql_postgres',
    sql="""
        SELECT 
            a.id, a.name, a.asset_code, a.vehicle_type, a.status,
            a.acquisition_date, a.last_maintenance_date,
            COUNT(DISTINCT wo.id) as total_work_orders,
            COUNT(DISTINCT CASE WHEN wo.status = 'COMPLETED' THEN wo.id END) as completed_work_orders,
            AVG(CASE WHEN wo.status = 'COMPLETED' THEN wo.actual_hours END) as avg_repair_hours,
            COUNT(DISTINCT mp.id) as maintenance_plans_count,
            MAX(wo.created_at) as last_work_order_date
        FROM assets_asset a
        LEFT JOIN work_orders_workorder wo ON wo.asset_id = a.id
        LEFT JOIN maintenance_maintenanceplan mp ON mp.asset_id = a.id
        WHERE a.status = 'ACTIVE'
        GROUP BY a.id
    """,
    bucket=BUCKET_NAME,
    filename='raw_data/assets_{{ ds }}.csv',
    export_format='csv',
    dag=dag,
)

extract_work_orders_data = PostgresToGCSOperator(
    task_id='extract_work_orders_data',
    postgres_conn_id='cloudsql_postgres',
    sql="""
        SELECT 
            wo.id, wo.asset_id, wo.work_order_type, wo.priority,
            wo.status, wo.created_at, wo.completed_at,
            wo.estimated_hours, wo.actual_hours,
            wo.description
        FROM work_orders_workorder wo
        WHERE wo.created_at >= NOW() - INTERVAL '2 years'
    """,
    bucket=BUCKET_NAME,
    filename='raw_data/work_orders_{{ ds }}.csv',
    export_format='csv',
    dag=dag,
)

# Task 2: Create Dataproc cluster
create_cluster = DataprocCreateClusterOperator(
    task_id='create_dataproc_cluster',
    project_id=PROJECT_ID,
    cluster_config=CLUSTER_CONFIG,
    region=REGION,
    cluster_name=CLUSTER_NAME,
    dag=dag,
)

# Task 3: Submit PySpark job for feature engineering
PYSPARK_JOB = {
    "reference": {"project_id": PROJECT_ID},
    "placement": {"cluster_name": CLUSTER_NAME},
    "pyspark_job": {
        "main_python_file_uri": f"gs://{BUCKET_NAME}/scripts/feature_engineering.py",
        "args": [
            f"--input-bucket={BUCKET_NAME}",
            f"--output-bucket={BUCKET_NAME}",
            "--date={{ ds }}",
        ],
    },
}

feature_engineering = DataprocSubmitJobOperator(
    task_id='feature_engineering',
    job=PYSPARK_JOB,
    region=REGION,
    project_id=PROJECT_ID,
    dag=dag,
)

# Task 4: Train ML model
def train_ml_model(**context):
    """Train the ML model using processed features"""
    import requests
    import json
    
    backend_url = Variable.get("backend_api_url", default_var="http://localhost:8000")
    api_token = Variable.get("backend_api_token")
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Call backend API to train model
        response = requests.post(
            f"{backend_url}/api/v1/predictions/ml-model/train/",
            headers=headers,
            timeout=600  # 10 minutes timeout
        )
        response.raise_for_status()
        
        result = response.json()
        logging.info(f"Model training completed: {result}")
        
        # Push metrics to XCom
        context['task_instance'].xcom_push(key='training_metrics', value=result.get('metrics'))
        context['task_instance'].xcom_push(key='model_version', value=result.get('version'))
        
        return result
    except Exception as e:
        logging.error(f"Error training model: {str(e)}")
        raise

train_model = PythonOperator(
    task_id='train_model',
    python_callable=train_ml_model,
    dag=dag,
)

# Task 5: Deploy model to Vertex AI
def deploy_to_vertex_ai(**context):
    """Deploy trained model to Vertex AI"""
    import requests
    
    backend_url = Variable.get("backend_api_url", default_var="http://localhost:8000")
    api_token = Variable.get("backend_api_token")
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    model_version = context['task_instance'].xcom_pull(task_ids='train_model', key='model_version')
    
    try:
        response = requests.post(
            f"{backend_url}/api/v1/predictions/ml-model/deploy/",
            headers=headers,
            json={
                'model_name': f'cmms-failure-prediction-{model_version}',
                'model_path': f'ml_models/failure_prediction_model_{model_version}.joblib'
            },
            timeout=600
        )
        response.raise_for_status()
        
        result = response.json()
        logging.info(f"Model deployed to Vertex AI: {result}")
        
        return result
    except Exception as e:
        logging.error(f"Error deploying model: {str(e)}")
        # Don't fail the DAG if deployment fails
        logging.warning("Continuing without Vertex AI deployment")
        return None

deploy_model = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_to_vertex_ai,
    dag=dag,
)

# Task 6: Delete Dataproc cluster
delete_cluster = DataprocDeleteClusterOperator(
    task_id='delete_dataproc_cluster',
    project_id=PROJECT_ID,
    cluster_name=CLUSTER_NAME,
    region=REGION,
    trigger_rule='all_done',  # Always delete cluster
    dag=dag,
)

# Task 7: Send success notification
def send_success_notification(**context):
    """Send email notification on successful completion"""
    metrics = context['task_instance'].xcom_pull(task_ids='train_model', key='training_metrics')
    model_version = context['task_instance'].xcom_pull(task_ids='train_model', key='model_version')
    
    subject = f"✅ ML Training Pipeline Completed - Version {model_version}"
    body = f"""
    <h2>ML Training Pipeline Completed Successfully</h2>
    <p><strong>Execution Date:</strong> {context['ds']}</p>
    <p><strong>Model Version:</strong> {model_version}</p>
    
    <h3>Training Metrics:</h3>
    <ul>
        <li><strong>Accuracy:</strong> {metrics.get('accuracy', 'N/A')}</li>
        <li><strong>Precision:</strong> {metrics.get('precision', 'N/A')}</li>
        <li><strong>Recall:</strong> {metrics.get('recall', 'N/A')}</li>
        <li><strong>F1 Score:</strong> {metrics.get('f1_score', 'N/A')}</li>
    </ul>
    
    <p>The model has been trained and is ready for predictions.</p>
    """
    
    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=body
    )

notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=send_success_notification,
    dag=dag,
)

# Define task dependencies
extract_assets_data >> create_cluster
extract_work_orders_data >> create_cluster
create_cluster >> feature_engineering >> train_model >> deploy_model >> delete_cluster >> notify_success
