"""
Report Generation DAG for CMMS System
Generates weekly KPI reports and sends via email
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.utils.email import send_email
from airflow.models import Variable
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import logging

# Configuration
BUCKET_NAME = Variable.get("gcs_bucket_name", default_var="cmms-reports")
SENDGRID_API_KEY = Variable.get("sendgrid_api_key", default_var="")

# Default arguments
default_args = {
    'owner': 'cmms-admin',
    'depends_on_past': False,
    'email': Variable.get("report_email", default_var="admin@cmms.com").split(','),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'weekly_kpi_report',
    default_args=default_args,
    description='Generate and send weekly KPI reports',
    schedule_interval='0 8 * * 1',  # Weekly on Monday at 8 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['reports', 'kpi', 'analytics'],
)

def extract_kpi_data(**context):
    """Extract KPI data from database"""
    postgres_hook = PostgresHook(postgres_conn_id='cloudsql_postgres')
    
    # Date range for the report (last 7 days)
    end_date = context['ds']
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
    
    queries = {
        'work_orders': f"""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending,
                AVG(CASE WHEN status = 'COMPLETED' THEN actual_hours END) as avg_completion_hours
            FROM work_orders_workorder
            WHERE created_at >= '{start_date}' AND created_at < '{end_date}'
        """,
        'mtbf': f"""
            SELECT 
                a.vehicle_type,
                COUNT(DISTINCT a.id) as asset_count,
                COUNT(wo.id) as failure_count,
                AVG(EXTRACT(EPOCH FROM (wo.created_at - LAG(wo.created_at) OVER (PARTITION BY a.id ORDER BY wo.created_at))) / 86400) as mtbf_days
            FROM assets_asset a
            LEFT JOIN work_orders_workorder wo ON wo.asset_id = a.id
            WHERE wo.work_order_type = 'CORRECTIVE'
            AND wo.created_at >= '{start_date}' AND wo.created_at < '{end_date}'
            GROUP BY a.vehicle_type
        """,
        'mttr': f"""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 3600) as mttr_hours
            FROM work_orders_workorder
            WHERE status = 'COMPLETED'
            AND completed_at IS NOT NULL
            AND created_at >= '{start_date}' AND created_at < '{end_date}'
        """,
        'inventory': f"""
            SELECT 
                COUNT(*) as total_parts,
                COUNT(CASE WHEN current_stock <= min_stock_level THEN 1 END) as low_stock_parts,
                SUM(current_stock * unit_cost) as total_inventory_value
            FROM inventory_sparepart
        """,
        'predictions': f"""
            SELECT 
                COUNT(*) as total_predictions,
                COUNT(CASE WHEN risk_level = 'HIGH' THEN 1 END) as high_risk,
                COUNT(CASE WHEN risk_level = 'CRITICAL' THEN 1 END) as critical_risk,
                AVG(failure_probability) as avg_failure_probability
            FROM predictions_failureprediction
            WHERE prediction_date >= '{start_date}' AND prediction_date < '{end_date}'
        """
    }
    
    kpi_data = {}
    connection = postgres_hook.get_conn()
    
    try:
        for key, query in queries.items():
            df = pd.read_sql(query, connection)
            kpi_data[key] = df.to_dict('records')[0] if not df.empty else {}
            logging.info(f"Extracted {key} data: {kpi_data[key]}")
        
        # Push to XCom
        context['task_instance'].xcom_push(key='kpi_data', value=kpi_data)
        context['task_instance'].xcom_push(key='date_range', value={'start': start_date, 'end': end_date})
        
        return kpi_data
    finally:
        connection.close()

extract_data = PythonOperator(
    task_id='extract_kpi_data',
    python_callable=extract_kpi_data,
    dag=dag,
)

def generate_charts(**context):
    """Generate charts for the report"""
    kpi_data = context['task_instance'].xcom_pull(task_ids='extract_kpi_data', key='kpi_data')
    
    charts = {}
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (10, 6)
    
    # Chart 1: Work Orders Status Distribution
    if kpi_data.get('work_orders'):
        wo_data = kpi_data['work_orders']
        fig, ax = plt.subplots()
        statuses = ['Completadas', 'En Progreso', 'Pendientes']
        values = [wo_data.get('completed', 0), wo_data.get('in_progress', 0), wo_data.get('pending', 0)]
        colors = ['#10B981', '#F59E0B', '#EF4444']
        
        ax.bar(statuses, values, color=colors)
        ax.set_title('Distribución de Órdenes de Trabajo', fontsize=14, fontweight='bold')
        ax.set_ylabel('Cantidad')
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        charts['work_orders'] = base64.b64encode(buffer.read()).decode()
        plt.close()
    
    # Chart 2: MTBF by Vehicle Type
    if kpi_data.get('mtbf'):
        mtbf_data = kpi_data['mtbf']
        if isinstance(mtbf_data, dict) and mtbf_data:
            fig, ax = plt.subplots()
            vehicle_types = list(mtbf_data.keys())
            mtbf_values = list(mtbf_data.values())
            
            ax.barh(vehicle_types, mtbf_values, color='#3B82F6')
            ax.set_title('MTBF por Tipo de Vehículo (días)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Días')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            charts['mtbf'] = base64.b64encode(buffer.read()).decode()
            plt.close()
    
    # Push to XCom
    context['task_instance'].xcom_push(key='charts', value=charts)
    
    return charts

generate_charts_task = PythonOperator(
    task_id='generate_charts',
    python_callable=generate_charts,
    dag=dag,
)

def generate_pdf_report(**context):
    """Generate PDF report (placeholder - would use reportlab or similar)"""
    kpi_data = context['task_instance'].xcom_pull(task_ids='extract_kpi_data', key='kpi_data')
    date_range = context['task_instance'].xcom_pull(task_ids='extract_kpi_data', key='date_range')
    
    # For now, we'll create a simple HTML report that can be converted to PDF
    # In production, use reportlab or weasyprint
    
    report_path = f"/tmp/cmms_report_{context['ds']}.html"
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #1F2937; }}
            h2 {{ color: #374151; margin-top: 30px; }}
            .kpi-box {{ 
                display: inline-block; 
                padding: 20px; 
                margin: 10px; 
                background: #F3F4F6; 
                border-radius: 8px;
                min-width: 200px;
            }}
            .kpi-value {{ font-size: 32px; font-weight: bold; color: #3B82F6; }}
            .kpi-label {{ font-size: 14px; color: #6B7280; }}
        </style>
    </head>
    <body>
        <h1>Reporte Semanal de KPIs - CMMS</h1>
        <p><strong>Período:</strong> {date_range['start']} a {date_range['end']}</p>
        
        <h2>Órdenes de Trabajo</h2>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('work_orders', {}).get('total', 0)}</div>
            <div class="kpi-label">Total</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('work_orders', {}).get('completed', 0)}</div>
            <div class="kpi-label">Completadas</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('work_orders', {}).get('avg_completion_hours', 0):.1f}h</div>
            <div class="kpi-label">Tiempo Promedio</div>
        </div>
        
        <h2>Métricas de Mantenimiento</h2>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('mttr', {}).get('mttr_hours', 0):.1f}h</div>
            <div class="kpi-label">MTTR (Tiempo Medio de Reparación)</div>
        </div>
        
        <h2>Inventario</h2>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('inventory', {}).get('total_parts', 0)}</div>
            <div class="kpi-label">Total de Repuestos</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('inventory', {}).get('low_stock_parts', 0)}</div>
            <div class="kpi-label">Stock Bajo</div>
        </div>
        
        <h2>Predicciones ML</h2>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('predictions', {}).get('high_risk', 0)}</div>
            <div class="kpi-label">Alto Riesgo</div>
        </div>
        <div class="kpi-box">
            <div class="kpi-value">{kpi_data.get('predictions', {}).get('critical_risk', 0)}</div>
            <div class="kpi-label">Riesgo Crítico</div>
        </div>
    </body>
    </html>
    """
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logging.info(f"Report generated at {report_path}")
    
    # Push to XCom
    context['task_instance'].xcom_push(key='report_path', value=report_path)
    
    return report_path

generate_pdf = PythonOperator(
    task_id='generate_pdf_report',
    python_callable=generate_pdf_report,
    dag=dag,
)

def upload_to_gcs(**context):
    """Upload report to Cloud Storage"""
    report_path = context['task_instance'].xcom_pull(task_ids='generate_pdf_report', key='report_path')
    
    # This will be handled by LocalFilesystemToGCSOperator
    return report_path

def send_report_email(**context):
    """Send report via SendGrid email"""
    kpi_data = context['task_instance'].xcom_pull(task_ids='extract_kpi_data', key='kpi_data')
    date_range = context['task_instance'].xcom_pull(task_ids='extract_kpi_data', key='date_range')
    charts = context['task_instance'].xcom_pull(task_ids='generate_charts', key='charts')
    
    subject = f"📊 Reporte Semanal CMMS - {date_range['start']} a {date_range['end']}"
    
    # Build charts HTML
    charts_html = ""
    if charts:
        for chart_name, chart_data in charts.items():
            charts_html += f'<img src="data:image/png;base64,{chart_data}" style="max-width: 100%; margin: 20px 0;"><br>'
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background: #1F2937; color: white; padding: 20px; }}
            .content {{ padding: 20px; }}
            .kpi-card {{ 
                display: inline-block; 
                padding: 15px; 
                margin: 10px; 
                background: #F3F4F6; 
                border-radius: 8px;
                min-width: 150px;
                text-align: center;
            }}
            .kpi-value {{ font-size: 28px; font-weight: bold; color: #3B82F6; }}
            .kpi-label {{ font-size: 12px; color: #6B7280; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Reporte Semanal CMMS</h1>
            <p>Período: {date_range['start']} a {date_range['end']}</p>
        </div>
        
        <div class="content">
            <h2>📋 Órdenes de Trabajo</h2>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('work_orders', {}).get('total', 0)}</div>
                <div class="kpi-label">Total</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('work_orders', {}).get('completed', 0)}</div>
                <div class="kpi-label">Completadas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('work_orders', {}).get('in_progress', 0)}</div>
                <div class="kpi-label">En Progreso</div>
            </div>
            
            <h2>⚙️ Métricas de Mantenimiento</h2>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('mttr', {}).get('mttr_hours', 0):.1f}h</div>
                <div class="kpi-label">MTTR</div>
            </div>
            
            <h2>📦 Inventario</h2>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('inventory', {}).get('total_parts', 0)}</div>
                <div class="kpi-label">Total Repuestos</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('inventory', {}).get('low_stock_parts', 0)}</div>
                <div class="kpi-label">Stock Bajo</div>
            </div>
            
            <h2>🔮 Predicciones ML</h2>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('predictions', {}).get('high_risk', 0)}</div>
                <div class="kpi-label">Alto Riesgo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{kpi_data.get('predictions', {}).get('critical_risk', 0)}</div>
                <div class="kpi-label">Crítico</div>
            </div>
            
            <h2>📈 Gráficos</h2>
            {charts_html}
            
            <p style="margin-top: 40px; color: #6B7280; font-size: 12px;">
                Este es un reporte automático generado por el sistema CMMS.
            </p>
        </div>
    </body>
    </html>
    """
    
    send_email(
        to=default_args['email'],
        subject=subject,
        html_content=body
    )
    
    logging.info("Report email sent successfully")

send_email_task = PythonOperator(
    task_id='send_report_email',
    python_callable=send_report_email,
    dag=dag,
)

# Upload to GCS task
upload_report = LocalFilesystemToGCSOperator(
    task_id='upload_report_to_gcs',
    src="{{ task_instance.xcom_pull(task_ids='generate_pdf_report', key='report_path') }}",
    dst=f"reports/weekly_report_{{{{ ds }}}}.html",
    bucket=BUCKET_NAME,
    dag=dag,
)

# Define task dependencies
extract_data >> generate_charts_task >> generate_pdf >> [upload_report, send_email_task]
