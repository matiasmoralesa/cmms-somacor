"""
Webhook delivery service
"""
import requests
import hmac
import hashlib
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Webhook, WebhookDelivery

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for delivering webhooks"""
    
    @staticmethod
    def generate_signature(payload: dict, secret: str) -> str:
        """Generate HMAC SHA256 signature for payload"""
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def deliver_webhook(webhook: Webhook, event_type: str, payload: dict) -> WebhookDelivery:
        """
        Deliver a webhook to the specified URL
        
        Args:
            webhook: Webhook instance
            event_type: Type of event (e.g., 'work_order.created')
            payload: Event data to send
        
        Returns:
            WebhookDelivery instance
        """
        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=webhook,
            event_type=event_type,
            payload=payload,
            status='pending'
        )
        
        # Prepare payload with metadata
        full_payload = {
            'event': event_type,
            'timestamp': timezone.now().isoformat(),
            'data': payload
        }
        
        # Generate signature
        signature = WebhookService.generate_signature(full_payload, webhook.secret)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature,
            'X-Webhook-Event': event_type,
            'X-Webhook-Delivery': str(delivery.id),
            'User-Agent': 'CMMS-Webhook/1.0'
        }
        
        # Attempt delivery
        start_time = datetime.now()
        try:
            response = requests.post(
                webhook.url,
                json=full_payload,
                headers=headers,
                timeout=30
            )
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Update delivery record
            delivery.status = 'success' if response.status_code < 400 else 'failed'
            delivery.http_status_code = response.status_code
            delivery.response_body = response.text[:1000]  # Limit response size
            delivery.delivered_at = timezone.now()
            delivery.duration_ms = duration_ms
            delivery.attempt_count += 1
            delivery.save()
            
            # Update webhook statistics
            webhook.total_deliveries += 1
            if delivery.status == 'success':
                webhook.successful_deliveries += 1
            else:
                webhook.failed_deliveries += 1
            webhook.last_delivery_at = timezone.now()
            webhook.last_delivery_status = delivery.status
            webhook.save()
            
            logger.info(
                f"Webhook delivered: {webhook.name} - {event_type} - "
                f"Status: {response.status_code} - Duration: {duration_ms}ms"
            )
            
        except requests.exceptions.RequestException as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Update delivery record with error
            delivery.status = 'failed'
            delivery.error_message = str(e)
            delivery.duration_ms = duration_ms
            delivery.attempt_count += 1
            
            # Schedule retry if within max retries
            if delivery.attempt_count < webhook.max_retries:
                delivery.status = 'retrying'
                delivery.next_retry_at = timezone.now() + timedelta(
                    seconds=webhook.retry_delay_seconds * delivery.attempt_count
                )
            
            delivery.save()
            
            # Update webhook statistics
            webhook.total_deliveries += 1
            webhook.failed_deliveries += 1
            webhook.last_delivery_at = timezone.now()
            webhook.last_delivery_status = delivery.status
            webhook.save()
            
            logger.error(
                f"Webhook delivery failed: {webhook.name} - {event_type} - "
                f"Error: {str(e)} - Attempt: {delivery.attempt_count}/{webhook.max_retries}"
            )
        
        return delivery
    
    @staticmethod
    def trigger_event(event_type: str, payload: dict):
        """
        Trigger webhooks for a specific event type
        
        Args:
            event_type: Type of event (e.g., 'work_order.created')
            payload: Event data to send
        """
        # Find all active webhooks subscribed to this event
        webhooks = Webhook.objects.filter(
            is_active=True,
            events__contains=[event_type]
        )
        
        logger.info(f"Triggering {webhooks.count()} webhooks for event: {event_type}")
        
        # Deliver to each webhook
        for webhook in webhooks:
            try:
                WebhookService.deliver_webhook(webhook, event_type, payload)
            except Exception as e:
                logger.error(f"Error delivering webhook {webhook.id}: {str(e)}")
    
    @staticmethod
    def retry_failed_deliveries():
        """
        Retry failed webhook deliveries that are due for retry
        This should be called periodically (e.g., via Celery task or cron)
        """
        now = timezone.now()
        pending_retries = WebhookDelivery.objects.filter(
            status='retrying',
            next_retry_at__lte=now
        )
        
        logger.info(f"Retrying {pending_retries.count()} failed webhook deliveries")
        
        for delivery in pending_retries:
            try:
                WebhookService.deliver_webhook(
                    delivery.webhook,
                    delivery.event_type,
                    delivery.payload
                )
            except Exception as e:
                logger.error(f"Error retrying delivery {delivery.id}: {str(e)}")
