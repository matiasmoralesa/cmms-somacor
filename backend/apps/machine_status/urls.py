from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetStatusViewSet

router = DefaultRouter()
router.register(r'', AssetStatusViewSet, basename='asset_status')

urlpatterns = [
    path('', include(router.urls)),
]
