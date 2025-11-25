"""Configuration URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'config'

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
