"""
Core URLs
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Admin endpoints (TEMPORAL)
    path('admin/makemigrations/', views.make_migrations, name='make-migrations'),
    path('admin/migrate/', views.run_migrations, name='run-migrations'),
    
    # Dashboard endpoints
    path('dashboard/', views.dashboard_data, name='dashboard-data'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('dashboard/maintenance-trend/', views.maintenance_trend, name='maintenance-trend'),
    path('dashboard/work-orders-by-priority/', views.work_orders_by_priority, name='work-orders-by-priority'),
    path('dashboard/asset-health/', views.asset_health, name='asset-health'),
]
