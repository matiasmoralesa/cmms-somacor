"""
URL configuration for images app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.images import views

router = DefaultRouter()
router.register(r'photos', views.InspectionPhotoViewSet, basename='inspection-photo')
router.register(r'analysis', views.ImageAnalysisResultViewSet, basename='image-analysis')
router.register(r'anomalies', views.VisualAnomalyViewSet, basename='visual-anomaly')
router.register(r'meter-readings', views.MeterReadingViewSet, basename='meter-reading')
router.register(r'damage-reports', views.DamageReportViewSet, basename='damage-report')

urlpatterns = [
    path('', include(router.urls)),
]
