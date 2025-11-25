"""Predictions URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'predictions'

router = DefaultRouter()
router.register(r'', views.FailurePredictionViewSet, basename='prediction')
router.register(r'alerts', views.AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
