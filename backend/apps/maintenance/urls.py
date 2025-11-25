"""Maintenance URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'maintenance'

router = DefaultRouter()
router.register(r'plans', views.MaintenancePlanViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
]
