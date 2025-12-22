"""
WebSocket Router for Brain AI LMS
Real-time communication endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import json
from datetime import datetime
import logging

from app.services.websocket_manager import (
    manager,
    chat_manager,
    websocket_endpoint
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_general(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    channel: str = Query("general")
):
    """General WebSocket connection for real-time updates"""
    user_id = None
    
    # Optionally validate token
    if token:
        try:
            from app.utils.password import decode_token
            payload = decode_token(token)
            user_id = int(payload.get("sub", 0))
        except Exception as e:
            logger.warning(f"WebSocket auth failed: {e}")
    
    await websocket_endpoint(
        websocket=websocket,
        channel=channel,
        user_id=user_id,
        group_id=None
    )


@router.websocket("/ws/chat/{group_id}")
async def websocket_chat(
    websocket: WebSocket,
    group_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket connection for study group chat"""
    user_id = None
    username = "Anonymous"
    
    # Validate token and get user info
    if token:
        try:
            from app.utils.password import decode_token
            payload = decode_token(token)
            user_id = int(payload.get("sub", 0))
            username = payload.get("email", "Anonymous")
        except Exception as e:
            logger.warning(f"WebSocket auth failed: {e}")
    
    await websocket_endpoint(
        websocket=websocket,
        channel="chat",
        user_id=user_id,
        group_id=f"group_{group_id}"
    )


@router.websocket("/ws/study-group/{group_id}")
async def websocket_study_group(
    websocket: WebSocket,
    group_id: str,
    token: str = Query(...)
):
    """WebSocket connection for study group with authentication"""
    user_id = None
    
    try:
        from app.utils.password import decode_token
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception as e:
        await websocket.close(code=4001)
        return
    
    await websocket_endpoint(
        websocket=websocket,
        channel="study_group",
        user_id=user_id,
        group_id=f"study_{group_id}"
    )


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """WebSocket connection for user notifications"""
    user_id = None
    
    try:
        from app.utils.password import decode_token
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0))
    except Exception as e:
        await websocket.close(code=4001)
        return
    
    await websocket_endpoint(
        websocket=websocket,
        channel="notifications",
        user_id=user_id,
        group_id=None
    )


@router.websocket("/ws/alumni")
async def websocket_alumni(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """WebSocket connection for alumni network"""
    user_id = None
    
    if token:
        try:
            from app.utils.password import decode_token
            payload = decode_token(token)
            user_id = int(payload.get("sub", 0))
        except Exception as e:
            logger.warning(f"WebSocket auth failed: {e}")
    
    await websocket_endpoint(
        websocket=websocket,
        channel="alumni",
        user_id=user_id,
        group_id=None
    )


@router.websocket("/ws/events/{event_id}")
async def websocket_events(
    websocket: WebSocket,
    event_id: str,
    token: Optional[str] = Query(None)
):
    """WebSocket connection for live events"""
    user_id = None
    
    if token:
        try:
            from app.utils.password import decode_token
            payload = decode_token(token)
            user_id = int(payload.get("sub", 0))
        except Exception as e:
            logger.warning(f"WebSocket auth failed: {e}")
    
    await websocket_endpoint(
        websocket=websocket,
        channel="events",
        user_id=user_id,
        group_id=f"event_{event_id}"
    )


# REST endpoints for WebSocket management
@router.get("/ws/connections")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        "total_connections": sum(
            len(connections) for connections in manager.active_connections.values()
        ),
        "channels": {
            channel: len(connections)
            for channel, connections in manager.active_connections.items()
        },
        "online_users": len(manager.get_online_users())
    }


@router.get("/ws/online-users")
async def get_online_users():
    """Get list of online user IDs"""
    return {"online_users": manager.get_online_users()}


@router.get("/ws/group-members/{group_id}")
async def get_group_members(group_id: str):
    """Get members of a specific group"""
    members = manager.get_group_members(f"study_{group_id}")
    return {
        "group_id": group_id,
        "members": members,
        "member_count": len(members)
    }


@router.get("/ws/chat/history/{group_id}")
async def get_chat_history(
    group_id: str,
    limit: int = 50
):
    """Get chat history for a group"""
    history = chat_manager.get_history(f"study_{group_id}", limit)
    return {
        "group_id": group_id,
        "history": history,
        "message_count": len(history)
    }


@router.post("/ws/chat/history/{group_id}/clear")
async def clear_chat_history(group_id: str):
    """Clear chat history for a group (admin only)"""
    chat_manager.clear_history(f"study_{group_id}")
    return {"status": "success", "message": f"Chat history cleared for group {group_id}"}


@router.post("/ws/broadcast")
async def broadcast_message(
    channel: str = "general",
    message: dict = {}
):
    """Broadcast a message to a channel (admin only)"""
    await manager.broadcast(
        message={
            "type": "broadcast",
            "data": message,
            "timestamp": datetime.utcnow().isoformat()
        },
        channel=channel
    )
    return {"status": "success", "channel": channel}


@router.post("/ws/notify/{user_id}")
async def send_personal_notification(
    user_id: int,
    notification: dict
):
    """Send a notification to a specific user"""
    from app.services.websocket_manager import notification_manager
    
    await notification_manager.send_notification(
        user_id=user_id,
        notification={
            **notification,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return {"status": "success", "user_id": user_id}


@router.get("/ws/events/active")
async def get_active_events():
    """Get list of active live events"""
    from app.services.websocket_manager import live_event_manager
    events = live_event_manager.get_active_events()
    return {"active_events": events}
