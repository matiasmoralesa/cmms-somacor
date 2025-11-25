"""Reports URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reports'

router = DefaultRouter()
router.register(r'', views.ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
