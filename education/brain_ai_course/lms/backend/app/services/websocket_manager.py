"""
WebSocket Manager for Real-time Features in Brain AI LMS
Handles WebSocket connections for chat, notifications, and live updates
"""

import json
import asyncio
from typing import Dict, Set, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection manager for handling WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections for the application"""
    
    def __init__(self):
        # Active connections grouped by type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "general": set(),
            "chat": set(),
            "notifications": set(),
            "study_group": set(),
            "alumni": set(),
            "events": set(),
        }
        # User-specific connections (user_id -> WebSocket)
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        # Group-specific connections (group_id -> Set[WebSocket])
        self.group_connections: Dict[str, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "general",
        user_id: Optional[int] = None,
        group_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to channel
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        
        # Store connection metadata
        conn_info = {
            "user_id": user_id,
            "channel": channel,
            "group_id": group_id,
            "connected_at": datetime.utcnow().isoformat(),
            "ip_address": None,
            "user_agent": None
        }
        if metadata:
            conn_info.update(metadata)
        self.connection_metadata[websocket] = conn_info
        
        # Track user-specific connection
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        # Track group-specific connection
        if group_id:
            if group_id not in self.group_connections:
                self.group_connections[group_id] = set()
            self.group_connections[group_id].add(websocket)
        
        logger.info(f"WebSocket connected: channel={channel}, user={user_id}, group={group_id}")
    
    def disconnect(
        self,
        websocket: WebSocket,
        channel: str = "general",
        user_id: Optional[int] = None,
        group_id: Optional[str] = None
    ):
        """Remove a WebSocket connection"""
        # Remove from channel
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from group connections
        if group_id and group_id in self.group_connections:
            self.group_connections[group_id].discard(websocket)
            if not self.group_connections[group_id]:
                del self.group_connections[group_id]
        
        # Remove metadata
        self.connection_metadata.pop(websocket, None)
        
        logger.info(f"WebSocket disconnected: channel={channel}, user={user_id}")
    
    async def send_personal_message(
        self,
        message: dict,
        user_id: int
    ):
        """Send a message to a specific user across all their connections"""
        if user_id in self.user_connections:
            disconnected = []
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending personal message: {e}")
                    disconnected.append(websocket)
            
            # Clean up disconnected websockets
            for ws in disconnected:
                self.user_connections[user_id].discard(ws)
    
    async def broadcast(
        self,
        message: dict,
        channel: str = "general",
        exclude: Optional[Set[WebSocket]] = None
    ):
        """Broadcast a message to all connections in a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = []
        for websocket in self.active_connections[channel]:
            if exclude and websocket in exclude:
                continue
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.active_connections[channel].discard(ws)
    
    async def broadcast_to_group(
        self,
        message: dict,
        group_id: str
    ):
        """Broadcast a message to all connections in a group"""
        if group_id not in self.group_connections:
            return
        
        disconnected = []
        for websocket in self.group_connections[group_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to group: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.group_connections[group_id].discard(ws)
    
    def get_connection_count(self, channel: str = "general") -> int:
        """Get the number of active connections in a channel"""
        return len(self.active_connections.get(channel, set()))
    
    def get_online_users(self) -> List[int]:
        """Get list of online user IDs"""
        return list(self.user_connections.keys())
    
    def get_group_members(self, group_id: str) -> List[dict]:
        """Get list of members in a group"""
        if group_id not in self.group_connections:
            return []
        
        members = []
        for websocket in self.group_connections[group_id]:
            metadata = self.connection_metadata.get(websocket, {})
            if metadata.get("user_id"):
                members.append({
                    "user_id": metadata["user_id"],
                    "connected_at": metadata.get("connected_at")
                })
        return members


# Global connection manager instance
manager = ConnectionManager()


# Chat message handling
class ChatManager:
    """Manages chat functionality for study groups and community"""
    
    def __init__(self, max_messages: int = 100):
        self.message_history: Dict[str, List[dict]] = {}
        self.max_messages = max_messages
    
    def add_message(
        self,
        group_id: str,
        user_id: int,
        username: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[dict] = None
    ) -> dict:
        """Add a message to the chat history"""
        if group_id not in self.message_history:
            self.message_history[group_id] = []
        
        message = {
            "id": f"msg_{datetime.utcnow().timestamp()}",
            "group_id": group_id,
            "user_id": user_id,
            "username": username,
            "content": content,
            "message_type": message_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.message_history[group_id].append(message)
        
        # Trim old messages
        if len(self.message_history[group_id]) > self.max_messages:
            self.message_history[group_id] = self.message_history[group_id][-self.max_messages:]
        
        return message
    
    def get_history(self, group_id: str, limit: int = 50) -> List[dict]:
        """Get chat history for a group"""
        if group_id not in self.message_history:
            return []
        
        return self.message_history[group_id][-limit:]
    
    def clear_history(self, group_id: str):
        """Clear chat history for a group"""
        if group_id in self.message_history:
            self.message_history[group_id] = []


# Global chat manager instance
chat_manager = ChatManager()


# WebSocket endpoint handlers
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str = "general",
    user_id: Optional[int] = None,
    group_id: Optional[str] = None
):
    """Main WebSocket endpoint handler"""
    await manager.connect(
        websocket=websocket,
        channel=channel,
        user_id=user_id,
        group_id=group_id
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type", "message")
            
            if message_type == "message":
                # Chat message
                content = data.get("content", "")
                username = data.get("username", "Anonymous")
                
                # Add to chat history
                if group_id:
                    chat_manager.add_message(
                        group_id=group_id,
                        user_id=user_id or 0,
                        username=username,
                        content=content
                    )
                    
                    # Broadcast to group
                    message = {
                        "type": "message",
                        "content": content,
                        "username": username,
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.broadcast_to_group(message, group_id)
            
            elif message_type == "typing":
                # User typing indicator
                if group_id:
                    message = {
                        "type": "typing",
                        "user_id": user_id,
                        "username": data.get("username", ""),
                        "is_typing": data.get("is_typing", True)
                    }
                    await manager.broadcast_to_group(message, group_id)
            
            elif message_type == "join":
                # User joined group
                if group_id:
                    message = {
                        "type": "system",
                        "content": f"{data.get('username', 'A user')} joined the chat",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.broadcast_to_group(message, group_id)
            
            elif message_type == "leave":
                # User left group
                if group_id:
                    message = {
                        "type": "system",
                        "content": f"{data.get('username', 'A user')} left the chat",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.broadcast_to_group(message, group_id)
    
    except WebSocketDisconnect:
        manager.disconnect(
            websocket=websocket,
            channel=channel,
            user_id=user_id,
            group_id=group_id
        )
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(
            websocket=websocket,
            channel=channel,
            user_id=user_id,
            group_id=group_id
        )


# Notification handling
class NotificationManager:
    """Manages real-time notifications"""
    
    def __init__(self):
        self.pending_notifications: Dict[int, List[dict]] = {}
    
    async def send_notification(
        self,
        user_id: int,
        notification: dict
    ):
        """Send a notification to a specific user"""
        # Add to pending notifications
        if user_id not in self.pending_notifications:
            self.pending_notifications[user_id] = []
        self.pending_notifications[user_id].append(notification)
        
        # Send via WebSocket if user is online
        await manager.send_personal_message(
            message={
                "type": "notification",
                "data": notification
            },
            user_id=user_id
        )
    
    def get_pending(self, user_id: int) -> List[dict]:
        """Get pending notifications for a user"""
        return self.pending_notifications.get(user_id, [])
    
    def clear_pending(self, user_id: int):
        """Clear pending notifications for a user"""
        self.pending_notifications[user_id] = []
    
    async def broadcast_notification(
        self,
        notification: dict,
        channels: List[str] = None
    ):
        """Broadcast a notification to multiple channels"""
        channel_list = channels or ["notifications"]
        
        for channel in channel_list:
            await manager.broadcast(
                message={
                    "type": "notification",
                    "data": notification
                },
                channel=channel
            )


# Notification types
NOTIFICATION_TYPES = {
    "course_update": "Course Update",
    "new_lesson": "New Lesson Available",
    "assignment_due": "Assignment Due",
    "grade_posted": "Grade Posted",
    "event_reminder": "Event Reminder",
    "study_group_invite": "Study Group Invite",
    "mentor_message": "Mentor Message",
    "certificate_ready": "Certificate Ready",
    "payment_received": "Payment Received",
    "general": "General Notification"
}


# Live event handling
class LiveEventManager:
    """Manages live events and webinars"""
    
    def __init__(self):
        self.active_events: Dict[str, dict] = {}
        self.participants: Dict[str, Set[int]] = {}
    
    def start_event(
        self,
        event_id: str,
        title: str,
        host_id: int,
        scheduled_duration: int = 60
    ):
        """Start a live event"""
        self.active_events[event_id] = {
            "id": event_id,
            "title": title,
            "host_id": host_id,
            "started_at": datetime.utcnow().isoformat(),
            "scheduled_duration": scheduled_duration,
            "status": "live"
        }
        self.participants[event_id] = set()
    
    def end_event(self, event_id: str):
        """End a live event"""
        if event_id in self.active_events:
            self.active_events[event_id]["status"] = "ended"
            self.active_events[event_id]["ended_at"] = datetime.utcnow().isoformat()
    
    def join_event(self, event_id: str, user_id: int) -> bool:
        """Add a participant to an event"""
        if event_id in self.active_events:
            self.participants[event_id].add(user_id)
            return True
        return False
    
    def leave_event(self, event_id: str, user_id: int):
        """Remove a participant from an event"""
        if event_id in self.participants:
            self.participants[event_id].discard(user_id)
    
    def get_participant_count(self, event_id: str) -> int:
        """Get the number of participants in an event"""
        return len(self.participants.get(event_id, set()))
    
    def get_active_events(self) -> List[dict]:
        """Get all active events"""
        return [
            {**event, "participants": self.get_participant_count(event_id)}
            for event_id, event in self.active_events.items()
            if event.get("status") == "live"
        ]


# Global instances
notification_manager = NotificationManager()
live_event_manager = LiveEventManager()
