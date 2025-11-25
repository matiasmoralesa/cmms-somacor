"""URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/assets/', include('apps.assets.urls')),
    path('api/v1/work-orders/', include('apps.work_orders.urls')),
    path('api/v1/maintenance/', include('apps.maintenance.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/checklists/', include('apps.checklists.urls')),
    path('api/v1/predictions/', include('apps.predictions.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/machine-status/', include('apps.machine_status.urls')),
    path('api/v1/core/', include('apps.core.urls')),
]
