"""
Telegram Bot Service for Notifications
"""
import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending notifications via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ''
        self.client_initialized = bool(self.bot_token)
        
        if not self.client_initialized:
            logger.warning("Telegram bot token not set. Telegram notifications disabled.")
        else:
            logger.info("Telegram service initialized")
    
    def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = 'HTML',
        disable_notification: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Parse mode (HTML, Markdown, MarkdownV2)
            disable_notification: Send silently
            
        Returns:
            Response dict or None if failed
        """
        if not self.client_initialized:
            logger.warning("Telegram service not initialized")
            return None
        
        url = f"{self.api_url}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Telegram message sent to {chat_id}")
                return result.get('result')
            else:
                logger.error(f"Telegram API error: {result.get('description')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return None

    def send_notification(
        self,
        chat_id: str,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'MEDIUM',
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a formatted notification to Telegram
        
        Args:
            chat_id: Telegram chat ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            data: Additional data
            
        Returns:
            Response dict or None if failed
        """
        # Format message with HTML
        priority_emoji = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🔵'
        }
        
        emoji = priority_emoji.get(priority, 'ℹ️')
        
        formatted_text = f"""
{emoji} <b>{title}</b>

{message}

<i>Prioridad: {priority}</i>
<i>Tipo: {notification_type}</i>
"""
        
        # Add additional data if present
        if data:
            if data.get('work_order_number'):
                formatted_text += f"\n📋 Orden: {data['work_order_number']}"
            if data.get('asset_name'):
                formatted_text += f"\n📦 Activo: {data['asset_name']}"
        
        # Send silently for LOW priority
        disable_notification = (priority == 'LOW')
        
        return self.send_message(
            chat_id=chat_id,
            text=formatted_text.strip(),
            parse_mode='HTML',
            disable_notification=disable_notification
        )
    
    def get_bot_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the bot"""
        if not self.client_initialized:
            return None
        
        url = f"{self.api_url}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                return result.get('result')
            else:
                logger.error(f"Telegram API error: {result.get('description')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get bot info: {str(e)}")
            return None
    
    def set_webhook(self, webhook_url: str) -> bool:
        """
        Set webhook for receiving updates
        
        Args:
            webhook_url: URL for webhook
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client_initialized:
            return False
        
        url = f"{self.api_url}/setWebhook"
        
        payload = {
            'url': webhook_url
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Webhook set to {webhook_url}")
                return True
            else:
                logger.error(f"Failed to set webhook: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set webhook: {str(e)}")
            return False
    
    def delete_webhook(self) -> bool:
        """Delete webhook"""
        if not self.client_initialized:
            return False
        
        url = f"{self.api_url}/deleteWebhook"
        
        try:
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('ok'):
                logger.info("Webhook deleted")
                return True
            else:
                logger.error(f"Failed to delete webhook: {result.get('description')}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete webhook: {str(e)}")
            return False


# Singleton instance
_telegram_service = None

def get_telegram_service() -> TelegramService:
    """Get or create TelegramService singleton instance"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
