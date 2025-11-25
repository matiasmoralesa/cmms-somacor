"""Inventory URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'inventory'

router = DefaultRouter()
router.register(r'spare-parts', views.SparePartViewSet, basename='sparepart')
router.register(r'stock-movements', views.StockMovementViewSet, basename='stockmovement')

urlpatterns = [
    path('', include(router.urls)),
]
