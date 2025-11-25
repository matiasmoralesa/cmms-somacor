"""
Google Cloud Pub/Sub Service for Notifications
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from google.cloud import pubsub_v1
from google.api_core import retry

logger = logging.getLogger(__name__)


class PubSubService:
    """Service for publishing notifications to Pub/Sub"""
    
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID', '')
        self.topic_name = os.getenv('PUBSUB_NOTIFICATIONS_TOPIC', 'cmms-notifications')
        self.client_initialized = False
        
        if self.project_id:
            try:
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
                self.client_initialized = True
                logger.info(f"Pub/Sub client initialized for topic: {self.topic_path}")
            except Exception as e:
                logger.error(f"Failed to initialize Pub/Sub client: {str(e)}")
        else:
            logger.warning("GCP_PROJECT_ID not set. Pub/Sub notifications disabled.")
    
    def create_topic_if_not_exists(self):
        """Create Pub/Sub topic if it doesn't exist"""
        if not self.client_initialized:
            return False
        
        try:
            self.publisher.get_topic(request={"topic": self.topic_path})
            logger.info(f"Topic {self.topic_name} already exists")
            return True
        except Exception:
            try:
                self.publisher.create_topic(request={"name": self.topic_path})
                logger.info(f"Created topic: {self.topic_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to create topic: {str(e)}")
                return False

    def publish_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'MEDIUM',
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Publish a notification to Pub/Sub
        
        Args:
            user_id: User ID to send notification to
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            data: Additional data
            
        Returns:
            Message ID if successful, None otherwise
        """
        if not self.client_initialized:
            logger.warning("Pub/Sub not initialized. Skipping notification publish.")
            return None
        
        try:
            notification_data = {
                'user_id': str(user_id),
                'notification_type': notification_type,
                'title': title,
                'message': message,
                'priority': priority,
                'data': data or {}
            }
            
            # Convert to JSON and encode
            message_json = json.dumps(notification_data)
            message_bytes = message_json.encode('utf-8')
            
            # Publish with retry
            future = self.publisher.publish(
                self.topic_path,
                message_bytes,
                user_id=str(user_id),
                notification_type=notification_type,
                priority=priority
            )
            
            # Wait for publish to complete
            message_id = future.result(timeout=30)
            
            logger.info(f"Published notification {message_id} for user {user_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to publish notification: {str(e)}")
            return None
    
    def publish_bulk_notifications(self, notifications: list) -> Dict[str, Any]:
        """
        Publish multiple notifications in bulk
        
        Args:
            notifications: List of notification dicts
            
        Returns:
            Dict with success/failure counts
        """
        if not self.client_initialized:
            logger.warning("Pub/Sub not initialized. Skipping bulk publish.")
            return {'success': 0, 'failed': len(notifications)}
        
        success_count = 0
        failed_count = 0
        message_ids = []
        
        for notification in notifications:
            message_id = self.publish_notification(
                user_id=notification.get('user_id'),
                notification_type=notification.get('notification_type'),
                title=notification.get('title'),
                message=notification.get('message'),
                priority=notification.get('priority', 'MEDIUM'),
                data=notification.get('data')
            )
            
            if message_id:
                success_count += 1
                message_ids.append(message_id)
            else:
                failed_count += 1
        
        return {
            'success': success_count,
            'failed': failed_count,
            'message_ids': message_ids
        }


# Singleton instance
_pubsub_service = None

def get_pubsub_service() -> PubSubService:
    """Get or create PubSubService singleton instance"""
    global _pubsub_service
    if _pubsub_service is None:
        _pubsub_service = PubSubService()
    return _pubsub_service
