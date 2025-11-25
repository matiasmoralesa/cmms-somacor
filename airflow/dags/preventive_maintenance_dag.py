"""
Preventive Maintenance DAG for CMMS System
Generates work orders for due maintenance plans daily at 6 AM
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.email import send_email
from airflow.models import Variable
import requests
import logging

# Configuration
BACKEND_URL = Variable.get("backend_api_url", default_var="http://localhost:8000")
API_TOKEN = Variable.get("backend_api_token")

# Default arguments
default_args = {
    'owner': 'cmms-admin',
    'depends_on_past': False,
    'email': Variable.get("alert_email", default_var="admin@cmms.com").split(','),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'preventive_maintenance_generator',
    default_args=default_args,
    description='Generate work orders for due preventive maintenance',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['maintenance', 'work-orders', 'automation'],
)

def get_due_maintenance_plans(**context):
    """Query database for maintenance plans that are due"""
    postgres_hook = PostgresHook(postgres_conn_id='cloudsql_postgres')
    
    query = """
        SELECT 
            mp.id,
            mp.name,
            mp.asset_id,
            a.name as asset_name,
            a.asset_code,
            mp.maintenance_type,
            mp.description,
            mp.estimated_hours,
            mp.next_due_date,
            mp.recurrence_interval,
            mp.recurrence_unit
        FROM maintenance_maintenanceplan mp
        JOIN assets_asset a ON a.id = mp.asset_id
        WHERE mp.is_active = true
        AND mp.next_due_date <= CURRENT_DATE
        AND a.status = 'ACTIVE'
        ORDER BY mp.next_due_date ASC
    """
    
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        plans = [dict(zip(columns, row)) for row in results]
        
        logging.info(f"Found {len(plans)} maintenance plans due")
        
        # Push to XCom
        context['task_instance'].xcom_push(key='due_plans', value=plans)
        
        return plans
    finally:
        cursor.close()
        connection.close()

query_due_plans = PythonOperator(
    task_id='query_due_maintenance_plans',
    python_callable=get_due_maintenance_plans,
    dag=dag,
)

def create_work_orders(**context):
    """Create work orders for due maintenance plans via Backend API"""
    plans = context['task_instance'].xcom_pull(task_ids='query_due_maintenance_plans', key='due_plans')
    
    if not plans:
        logging.info("No maintenance plans due. Skipping work order creation.")
        return {'created': 0, 'failed': 0}
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    created_count = 0
    failed_count = 0
    created_work_orders = []
    
    for plan in plans:
        try:
            # Create work order payload
            payload = {
                'asset': plan['asset_id'],
                'title': f"Mantenimiento Preventivo: {plan['name']}",
                'description': plan['description'] or f"Mantenimiento preventivo programado para {plan['asset_name']}",
                'work_order_type': 'PREVENTIVE',
                'priority': 'MEDIUM',
                'estimated_hours': plan['estimated_hours'] or 2.0,
                'maintenance_plan': plan['id']
            }
            
            # Call Backend API
            response = requests.post(
                f"{BACKEND_URL}/api/v1/work-orders/work-orders/",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            work_order = response.json()
            created_work_orders.append({
                'work_order_id': work_order['id'],
                'work_order_number': work_order.get('work_order_number'),
                'asset_name': plan['asset_name'],
                'plan_name': plan['name']
            })
            
            created_count += 1
            logging.info(f"Created work order for plan {plan['id']}: {work_order.get('work_order_number')}")
            
        except Exception as e:
            failed_count += 1
            logging.error(f"Failed to create work order for plan {plan['id']}: {str(e)}")
    
    result = {
        'created': created_count,
        'failed': failed_count,
        'work_orders': created_work_orders
    }
    
    # Push to XCom
    context['task_instance'].xcom_push(key='creation_result', value=result)
    
    logging.info(f"Work order creation completed: {created_count} created, {failed_count} failed")
    
    return result

create_work_orders_task = PythonOperator(
    task_id='create_work_orders',
    python_callable=create_work_orders,
    dag=dag,
)

def publish_notifications(**context):
    """Publish notifications via Pub/Sub for created work orders"""
    result = context['task_instance'].xcom_pull(task_ids='create_work_orders', key='creation_result')
    
    if result['created'] == 0:
        logging.info("No work orders created. Skipping notifications.")
        return
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    for wo in result['work_orders']:
        try:
            # Create notification via Backend API
            notification_payload = {
                'title': 'Nueva Orden de Trabajo Preventiva',
                'message': f"Se ha creado la orden {wo['work_order_number']} para {wo['asset_name']}",
                'notification_type': 'WORK_ORDER_CREATED',
                'work_order': wo['work_order_id']
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/notifications/",
                headers=headers,
                json=notification_payload,
                timeout=10
            )
            response.raise_for_status()
            
            logging.info(f"Notification sent for work order {wo['work_order_number']}")
            
        except Exception as e:
            logging.error(f"Failed to send notification for work order {wo['work_order_id']}: {str(e)}")

publish_notifications_task = PythonOperator(
    task_id='publish_notifications',
    python_callable=publish_notifications,
    dag=dag,
)

def send_summary_email(**context):
    """Send summary email with created work orders"""
    result = context['task_instance'].xcom_pull(task_ids='create_work_orders', key='creation_result')
    
    if result['created'] == 0 and result['failed'] == 0:
        logging.info("No maintenance plans were due. Skipping email.")
        return
    
    subject = f"📋 Resumen de Mantenimiento Preventivo - {context['ds']}"
    
    work_orders_html = ""
    if result['work_orders']:
        work_orders_html = "<ul>"
        for wo in result['work_orders']:
            work_orders_html += f"<li><strong>{wo['work_order_number']}</strong> - {wo['asset_name']} ({wo['plan_name']})</li>"
        work_orders_html += "</ul>"
    
    body = f"""
    <h2>Resumen de Generación de Órdenes de Trabajo Preventivas</h2>
    <p><strong>Fecha:</strong> {context['ds']}</p>
    
    <h3>Estadísticas:</h3>
    <ul>
        <li><strong>Órdenes Creadas:</strong> {result['created']}</li>
        <li><strong>Fallos:</strong> {result['failed']}</li>
    </ul>
    
    {f"<h3>Órdenes de Trabajo Creadas:</h3>{work_orders_html}" if work_orders_html else ""}
    
    <p>Las órdenes de trabajo han sido creadas y asignadas automáticamente.</p>
    <p>Los técnicos han sido notificados a través del sistema.</p>
    """
    
    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=body
    )

send_summary = PythonOperator(
    task_id='send_summary_email',
    python_callable=send_summary_email,
    dag=dag,
)

# Define task dependencies
query_due_plans >> create_work_orders_task >> publish_notifications_task >> send_summary
