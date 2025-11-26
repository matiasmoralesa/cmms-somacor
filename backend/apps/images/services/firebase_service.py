"""
Firebase integration service for real-time chat and notifications.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore, messaging
from django.conf import settings

logger = logging.getLogger(__name__)


class FirebaseService:
    """
    Service class for Firebase operations including Firestore and Cloud Messaging.
    Implements chat rooms, messages, user presence, and push notifications.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase Admin SDK if not already initialized."""
        if not self._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials."""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                cred_path = settings.FIREBASE_CREDENTIALS_PATH
                
                if not cred_path or not os.path.exists(cred_path):
                    logger.warning("Firebase credentials not found. Firebase features will be disabled.")
                    self.db = None
                    return
                
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': settings.FIREBASE_DATABASE_URL,
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
                })
                logger.info("Firebase Admin SDK initialized successfully")
            
            self.db = firestore.client()
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            self.db = None
    
    def is_available(self) -> bool:
        """Check if Firebase is properly initialized and available."""
        return self.db is not None
    
    # ========================================================================
    # CHAT ROOM OPERATIONS
    # ========================================================================
    
    def create_chat_room(self, work_order_id: str, participants: List[str], 
                        asset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new chat room for a work order.
        
        Args:
            work_order_id: ID of the work order
            participants: List of user IDs who can access the room
            asset_id: Optional asset ID associated with the room
            
        Returns:
            Dict containing the created chat room data
        """
        if not self.is_available():
            raise RuntimeError("Firebase is not available")
        
        try:
            room_data = {
                'workOrderId': work_order_id,
                'assetId': asset_id,
                'participants': participants,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'lastMessageAt': firestore.SERVER_TIMESTAMP,
                'lastMessage': None,
            }
            
            # Use work_order_id as the room ID
            room_ref = self.db.collection('chat_rooms').document(work_order_id)
            room_ref.set(room_data)
            
            logger.info(f"Created chat room for work order {work_order_id}")
            return {'id': work_order_id, **room_data}
            
        except Exception as e:
            logger.error(f"Failed to create chat room: {str(e)}")
            raise
    
    def get_chat_room(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get chat room data by ID."""
        if not self.is_available():
            return None
        
        try:
            room_ref = self.db.collection('chat_rooms').document(room_id)
            room = room_ref.get()
            
            if room.exists:
                return {'id': room.id, **room.to_dict()}
            return None
            
        except Exception as e:
            logger.error(f"Failed to get chat room: {str(e)}")
            return None
    
    def add_participant(self, room_id: str, user_id: str) -> bool:
        """Add a participant to a chat room."""
        if not self.is_available():
            return False
        
        try:
            room_ref = self.db.collection('chat_rooms').document(room_id)
            room_ref.update({
                'participants': firestore.ArrayUnion([user_id])
            })
            logger.info(f"Added user {user_id} to room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add participant: {str(e)}")
            return False
    
    def remove_participant(self, room_id: str, user_id: str) -> bool:
        """Remove a participant from a chat room."""
        if not self.is_available():
            return False
        
        try:
            room_ref = self.db.collection('chat_rooms').document(room_id)
            room_ref.update({
                'participants': firestore.ArrayRemove([user_id])
            })
            logger.info(f"Removed user {user_id} from room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove participant: {str(e)}")
            return False
    
    # ========================================================================
    # MESSAGE OPERATIONS
    # ========================================================================
    
    def send_message(self, room_id: str, sender_id: str, sender_name: str,
                    sender_role: str, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a chat room.
        
        Args:
            room_id: ID of the chat room
            sender_id: ID of the user sending the message
            sender_name: Name of the sender
            sender_role: Role of the sender
            text: Message text content
            image_url: Optional URL of attached image
            
        Returns:
            Dict containing the created message data
        """
        if not self.is_available():
            raise RuntimeError("Firebase is not available")
        
        try:
            message_data = {
                'roomId': room_id,
                'senderId': sender_id,
                'senderName': sender_name,
                'senderRole': sender_role,
                'text': text,
                'imageUrl': image_url,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'readBy': [sender_id],  # Sender has read their own message
                'edited': False,
            }
            
            # Add message to subcollection
            messages_ref = self.db.collection('chat_rooms').document(room_id).collection('messages')
            message_ref = messages_ref.add(message_data)
            
            # Update room's last message
            room_ref = self.db.collection('chat_rooms').document(room_id)
            room_ref.update({
                'lastMessageAt': firestore.SERVER_TIMESTAMP,
                'lastMessage': {
                    'text': text,
                    'senderId': sender_id,
                    'timestamp': firestore.SERVER_TIMESTAMP,
                }
            })
            
            logger.info(f"Message sent to room {room_id} by user {sender_id}")
            return {'id': message_ref[1].id, **message_data}
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
    
    def get_chat_history(self, room_id: str, limit: int = 50, 
                        before_timestamp: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get chat message history for a room.
        
        Args:
            room_id: ID of the chat room
            limit: Maximum number of messages to retrieve
            before_timestamp: Get messages before this timestamp (for pagination)
            
        Returns:
            List of message dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            messages_ref = self.db.collection('chat_rooms').document(room_id).collection('messages')
            query = messages_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            if before_timestamp:
                query = query.where('timestamp', '<', before_timestamp)
            
            messages = query.stream()
            
            result = []
            for msg in messages:
                result.append({'id': msg.id, **msg.to_dict()})
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get chat history: {str(e)}")
            return []
    
    def mark_message_as_read(self, room_id: str, message_id: str, user_id: str) -> bool:
        """Mark a message as read by a user."""
        if not self.is_available():
            return False
        
        try:
            message_ref = self.db.collection('chat_rooms').document(room_id).collection('messages').document(message_id)
            message_ref.update({
                'readBy': firestore.ArrayUnion([user_id])
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark message as read: {str(e)}")
            return False
    
    # ========================================================================
    # USER PRESENCE OPERATIONS
    # ========================================================================
    
    def update_user_presence(self, user_id: str, online: bool, 
                           typing_in: Optional[str] = None) -> bool:
        """
        Update user's online presence and typing status.
        
        Args:
            user_id: ID of the user
            online: Whether user is online
            typing_in: Optional room ID where user is typing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            presence_data = {
                'userId': user_id,
                'online': online,
                'lastSeen': firestore.SERVER_TIMESTAMP,
            }
            
            if typing_in is not None:
                presence_data['typingIn'] = typing_in
            
            presence_ref = self.db.collection('user_presence').document(user_id)
            presence_ref.set(presence_data, merge=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user presence: {str(e)}")
            return False
    
    def get_user_presence(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's presence data."""
        if not self.is_available():
            return None
        
        try:
            presence_ref = self.db.collection('user_presence').document(user_id)
            presence = presence_ref.get()
            
            if presence.exists:
                return presence.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user presence: {str(e)}")
            return None
    
    # ========================================================================
    # PUSH NOTIFICATION OPERATIONS
    # ========================================================================
    
    def send_push_notification(self, user_id: str, notification_type: str,
                              title: str, body: str, data: Dict[str, Any],
                              device_tokens: List[str]) -> Dict[str, Any]:
        """
        Send push notification to user's devices.
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification (chat, work_order, anomaly, alert)
            title: Notification title
            body: Notification body text
            data: Additional data payload
            device_tokens: List of FCM device tokens
            
        Returns:
            Dict with success count and failed tokens
        """
        if not self.is_available():
            raise RuntimeError("Firebase is not available")
        
        if not device_tokens:
            logger.warning(f"No device tokens for user {user_id}")
            return {'success_count': 0, 'failed_tokens': []}
        
        try:
            # Create notification payload
            notification = messaging.Notification(
                title=title,
                body=body,
            )
            
            # Add notification type to data
            data['type'] = notification_type
            data['timestamp'] = datetime.utcnow().isoformat()
            
            # Send to multiple devices
            messages = [
                messaging.Message(
                    notification=notification,
                    data=data,
                    token=token,
                )
                for token in device_tokens
            ]
            
            response = messaging.send_all(messages)
            
            # Store notification in Firestore
            notification_data = {
                'userId': user_id,
                'type': notification_type,
                'title': title,
                'body': body,
                'data': data,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'sentAt': firestore.SERVER_TIMESTAMP,
                'successCount': response.success_count,
                'failureCount': response.failure_count,
            }
            
            self.db.collection('notifications').document(user_id).collection('sent').add(notification_data)
            
            logger.info(f"Sent {response.success_count} notifications to user {user_id}")
            
            # Collect failed tokens
            failed_tokens = [
                device_tokens[idx] for idx, resp in enumerate(response.responses) if not resp.success
            ]
            
            return {
                'success_count': response.success_count,
                'failed_tokens': failed_tokens,
            }
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            raise
    
    def register_device_token(self, user_id: str, device_token: str) -> bool:
        """Register a device token for push notifications."""
        if not self.is_available():
            return False
        
        try:
            presence_ref = self.db.collection('user_presence').document(user_id)
            presence_ref.set({
                'deviceTokens': firestore.ArrayUnion([device_token])
            }, merge=True)
            
            logger.info(f"Registered device token for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register device token: {str(e)}")
            return False
    
    def unregister_device_token(self, user_id: str, device_token: str) -> bool:
        """Unregister a device token."""
        if not self.is_available():
            return False
        
        try:
            presence_ref = self.db.collection('user_presence').document(user_id)
            presence_ref.update({
                'deviceTokens': firestore.ArrayRemove([device_token])
            })
            
            logger.info(f"Unregistered device token for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister device token: {str(e)}")
            return False


# Create singleton instance
firebase_service = FirebaseService()
