"""Work Orders URLs"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'work_orders'

router = DefaultRouter()
router.register(r'', views.WorkOrderViewSet, basename='workorder')

urlpatterns = [
    path('', include(router.urls)),
]
