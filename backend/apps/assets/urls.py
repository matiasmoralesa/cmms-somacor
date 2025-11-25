"""Assets URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'assets'

# Registrar locations y documents primero para evitar conflictos con el path vacío
router = DefaultRouter()
router.register(r'locations', views.LocationViewSet, basename='location')
router.register(r'documents', views.AssetDocumentViewSet, basename='document')
router.register(r'', views.AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
