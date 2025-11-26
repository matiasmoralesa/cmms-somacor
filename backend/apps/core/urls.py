"""
Core URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('migrate/', views.run_migrations, name='run-migrations'),
    path('health/', views.health_check, name='health-check'),
    path('sync-users/', views.sync_firebase_users, name='sync-firebase-users'),
    path('check-user/', views.check_user, name='check-user'),
]
