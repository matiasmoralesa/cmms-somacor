"""
Views for notifications app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceSerializer,
    BulkNotificationSerializer
)
from .pubsub_service import get_pubsub_service
from .telegram_service import get_telegram_service
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['notification_type', 'priority', 'is_read']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for current user"""
        return Notification.objects.filter(user=self.request.user).select_related(
            'work_order', 'asset', 'prediction'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'marked_read': updated})
    
    @action(detail=False, methods=['delete'])
    def clear_read(self, request):
        """Delete all read notifications"""
        deleted_count, _ = self.get_queryset().filter(is_read=True).delete()
        return Response({'deleted': deleted_count})
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create notifications for multiple users"""
        serializer = BulkNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user_ids = data['user_ids']
        
        notifications = []
        pubsub_service = get_pubsub_service()
        telegram_service = get_telegram_service()
        
        for user_id in user_ids:
            notification = Notification.objects.create(
                user_id=user_id,
                notification_type=data['notification_type'],
                priority=data['priority'],
                title=data['title'],
                message=data['message'],
                data=data.get('data', {})
            )
            notifications.append(notification)
            
            # Publish to Pub/Sub
            if pubsub_service.client_initialized:
                message_id = pubsub_service.publish_notification(
                    user_id=user_id,
                    notification_type=data['notification_type'],
                    title=data['title'],
                    message=data['message'],
                    priority=data['priority'],
                    data=data.get('data')
                )
                if message_id:
                    notification.pubsub_message_id = message_id
                    notification.save(update_fields=['pubsub_message_id'])
            
            # Send via Telegram if user has telegram_chat_id and preference enabled
            try:
                user = notification.user
                if hasattr(user, 'telegram_chat_id') and user.telegram_chat_id:
                    # Check preference
                    preference = NotificationPreference.objects.filter(
                        user=user,
                        notification_type=data['notification_type']
                    ).first()
                    
                    if preference and preference.telegram_enabled:
                        telegram_service.send_notification(
                            chat_id=user.telegram_chat_id,
                            notification_type=data['notification_type'],
                            title=data['title'],
                            message=data['message'],
                            priority=data['priority'],
                            data=data.get('data')
                        )
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {str(e)}")
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer
    
    def get_queryset(self):
        """Return preferences for current user"""
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user to current user on create"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Get or create default preferences for all notification types"""
        preferences = []
        
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            pref, created = NotificationPreference.objects.get_or_create(
                user=request.user,
                notification_type=notification_type,
                defaults={
                    'in_app_enabled': True,
                    'email_enabled': True,
                    'push_enabled': False,
                    'telegram_enabled': False
                }
            )
            preferences.append(pref)
        
        serializer = self.get_serializer(preferences, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_bulk(self, request):
        """Update multiple preferences at once"""
        preferences_data = request.data.get('preferences', [])
        
        updated = []
        for pref_data in preferences_data:
            notification_type = pref_data.get('notification_type')
            if not notification_type:
                continue
            
            pref, created = NotificationPreference.objects.update_or_create(
                user=request.user,
                notification_type=notification_type,
                defaults={
                    'in_app_enabled': pref_data.get('in_app_enabled', True),
                    'email_enabled': pref_data.get('email_enabled', True),
                    'push_enabled': pref_data.get('push_enabled', False),
                    'telegram_enabled': pref_data.get('telegram_enabled', False),
                    'quiet_hours_enabled': pref_data.get('quiet_hours_enabled', False),
                    'quiet_hours_start': pref_data.get('quiet_hours_start'),
                    'quiet_hours_end': pref_data.get('quiet_hours_end'),
                }
            )
            updated.append(pref)
        
        serializer = self.get_serializer(updated, many=True)
        return Response(serializer.data)



class TelegramViewSet(viewsets.ViewSet):
    """
    ViewSet for Telegram integration
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def bot_info(self, request):
        """Get Telegram bot information"""
        telegram_service = get_telegram_service()
        
        if not telegram_service.client_initialized:
            return Response(
                {'error': 'Telegram service not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        bot_info = telegram_service.get_bot_info()
        
        if bot_info:
            return Response(bot_info)
        else:
            return Response(
                {'error': 'Failed to get bot info'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def link_chat(self, request):
        """Link user's Telegram chat ID"""
        chat_id = request.data.get('chat_id')
        
        if not chat_id:
            return Response(
                {'error': 'chat_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update user's telegram_chat_id
        user = request.user
        user.telegram_chat_id = str(chat_id)
        user.save(update_fields=['telegram_chat_id'])
        
        # Send test message
        telegram_service = get_telegram_service()
        result = telegram_service.send_message(
            chat_id=str(chat_id),
            text="✅ <b>Cuenta vinculada exitosamente!</b>\n\nAhora recibirás notificaciones del sistema CMMS en este chat.",
            parse_mode='HTML'
        )
        
        if result:
            return Response({
                'message': 'Telegram chat linked successfully',
                'chat_id': chat_id
            })
        else:
            return Response(
                {'error': 'Failed to send test message'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def unlink_chat(self, request):
        """Unlink user's Telegram chat"""
        user = request.user
        user.telegram_chat_id = None
        user.save(update_fields=['telegram_chat_id'])
        
        return Response({
            'message': 'Telegram chat unlinked successfully'
        })
    
    @action(detail=False, methods=['post'])
    def test_notification(self, request):
        """Send a test notification to user's Telegram"""
        user = request.user
        
        if not hasattr(user, 'telegram_chat_id') or not user.telegram_chat_id:
            return Response(
                {'error': 'No Telegram chat linked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        telegram_service = get_telegram_service()
        result = telegram_service.send_notification(
            chat_id=user.telegram_chat_id,
            notification_type='SYSTEM',
            title='Notificación de Prueba',
            message='Esta es una notificación de prueba del sistema CMMS.',
            priority='MEDIUM'
        )
        
        if result:
            return Response({
                'message': 'Test notification sent successfully'
            })
        else:
            return Response(
                {'error': 'Failed to send test notification'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def set_webhook(self, request):
        """Set Telegram webhook URL"""
        webhook_url = request.data.get('webhook_url')
        
        if not webhook_url:
            return Response(
                {'error': 'webhook_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        telegram_service = get_telegram_service()
        success = telegram_service.set_webhook(webhook_url)
        
        if success:
            return Response({
                'message': 'Webhook set successfully',
                'webhook_url': webhook_url
            })
        else:
            return Response(
                {'error': 'Failed to set webhook'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def webhook_info(self, request):
        """Get webhook information"""
        import requests
        telegram_service = get_telegram_service()
        
        if not telegram_service.client_initialized:
            return Response(
                {'error': 'Telegram service not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        url = f"{telegram_service.api_url}/getWebhookInfo"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Response(response.json())
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
