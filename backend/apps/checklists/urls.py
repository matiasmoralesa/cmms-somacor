"""Checklists URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'checklists'

router = DefaultRouter()
router.register(r'templates', views.ChecklistTemplateViewSet, basename='template')
router.register(r'responses', views.ChecklistResponseViewSet, basename='response')

urlpatterns = [
    path('', include(router.urls)),
]
