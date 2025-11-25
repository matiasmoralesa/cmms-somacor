"""Google Cloud Pub/Sub utility"""
from google.cloud import pubsub_v1
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)


class GCPPubSubClient:
    """Client for Google Cloud Pub/Sub operations"""
    
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.publisher = pubsub_v1.PublisherClient() if self.project_id else None
        
        # Topic names
        self.topic_notifications = settings.GCP_PUBSUB_TOPIC_NOTIFICATIONS
        self.topic_events = settings.GCP_PUBSUB_TOPIC_EVENTS
        self.topic_alerts = settings.GCP_PUBSUB_TOPIC_ALERTS
    
    def _get_topic_path(self, topic_name):
        """Get full topic path"""
        return self.publisher.topic_path(self.project_id, topic_name)
    
    def publish_message(self, topic_name, message_data, **attributes):
        """
        Publish message to topic
        
        Args:
            topic_name: Topic name
            message_data: Message data (dict)
            **attributes: Additional message attributes
        
        Returns:
            str: Message ID
        """
        if not self.publisher:
            logger.warning("Pub/Sub not configured, skipping message publish")
            return None
        
        try:
            topic_path = self._get_topic_path(topic_name)
            
            # Convert message to JSON bytes
            message_bytes = json.dumps(message_data).encode('utf-8')
            
            # Publish message
            future = self.publisher.publish(
                topic_path,
                message_bytes,
                **attributes
            )
            
            message_id = future.result()
            logger.info(f"Published message {message_id} to {topic_name}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error publishing message to {topic_name}: {e}")
            return None
    
    def publish_notification(self, user_id, notification_type, title, message, data=None):
        """
        Publish notification message
        
        Args:
            user_id: User ID to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Additional data (dict)
        """
        message_data = {
            'user_id': str(user_id),
            'type': notification_type,
            'title': title,
            'message': message,
            'data': data or {}
        }
        
        return self.publish_message(
            self.topic_notifications,
            message_data,
            notification_type=notification_type
        )
    
    def publish_event(self, event_type, entity_type, entity_id, action, user_id, data=None):
        """
        Publish system event
        
        Args:
            event_type: Type of event (work_order, asset, etc.)
            entity_type: Entity type
            entity_id: Entity ID
            action: Action performed (created, updated, deleted)
            user_id: User who performed action
            data: Additional data
        """
        message_data = {
            'event_type': event_type,
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'action': action,
            'user_id': str(user_id),
            'data': data or {}
        }
        
        return self.publish_message(
            self.topic_events,
            message_data,
            event_type=event_type,
            action=action
        )
    
    def publish_alert(self, alert_type, severity, title, message, asset_id=None, data=None):
        """
        Publish alert message
        
        Args:
            alert_type: Type of alert
            severity: Alert severity (info, warning, error, critical)
            title: Alert title
            message: Alert message
            asset_id: Related asset ID (optional)
            data: Additional data
        """
        message_data = {
            'alert_type': alert_type,
            'severity': severity,
            'title': title,
            'message': message,
            'asset_id': str(asset_id) if asset_id else None,
            'data': data or {}
        }
        
        return self.publish_message(
            self.topic_alerts,
            message_data,
            alert_type=alert_type,
            severity=severity
        )


# Singleton instance
pubsub_client = GCPPubSubClient() if settings.GCP_PROJECT_ID else None


# Helper functions
def notify_work_order_created(work_order, created_by):
    """Notify when work order is created"""
    if not pubsub_client:
        return
    
    # Notify assigned user
    if work_order.assigned_to:
        pubsub_client.publish_notification(
            user_id=work_order.assigned_to.id,
            notification_type='work_order_assigned',
            title='Nueva Orden de Trabajo',
            message=f'Se te ha asignado la OT {work_order.work_order_number}: {work_order.title}',
            data={
                'work_order_id': str(work_order.id),
                'work_order_number': work_order.work_order_number
            }
        )
    
    # Publish event
    pubsub_client.publish_event(
        event_type='work_order',
        entity_type='WorkOrder',
        entity_id=work_order.id,
        action='created',
        user_id=created_by.id,
        data={'work_order_number': work_order.work_order_number}
    )


def notify_work_order_assigned(work_order, assigned_by):
    """Notify when work order is assigned"""
    if not pubsub_client or not work_order.assigned_to:
        return
    
    pubsub_client.publish_notification(
        user_id=work_order.assigned_to.id,
        notification_type='work_order_assigned',
        title='Orden de Trabajo Asignada',
        message=f'Se te ha asignado la OT {work_order.work_order_number}: {work_order.title}',
        data={
            'work_order_id': str(work_order.id),
            'work_order_number': work_order.work_order_number
        }
    )


def notify_work_order_completed(work_order, completed_by):
    """Notify when work order is completed"""
    if not pubsub_client:
        return
    
    # Notify creator
    if work_order.created_by:
        pubsub_client.publish_notification(
            user_id=work_order.created_by.id,
            notification_type='work_order_completed',
            title='Orden de Trabajo Completada',
            message=f'La OT {work_order.work_order_number} ha sido completada',
            data={
                'work_order_id': str(work_order.id),
                'work_order_number': work_order.work_order_number,
                'actual_hours': str(work_order.actual_hours)
            }
        )
    
    # Publish event
    pubsub_client.publish_event(
        event_type='work_order',
        entity_type='WorkOrder',
        entity_id=work_order.id,
        action='completed',
        user_id=completed_by.id,
        data={
            'work_order_number': work_order.work_order_number,
            'actual_hours': str(work_order.actual_hours)
        }
    )
