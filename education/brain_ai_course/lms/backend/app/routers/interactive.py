"""
Interactive Learning WebSocket Router
Handles real-time code execution, AI tutor chat, and peer review interactions
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import asyncio
import json
import logging
from datetime import datetime

from app.database import get_db
from app.models.user import User, UserRole
from app.services.code_execution_service import code_execution_manager, CodeExecutionRequest, ExecutionLanguage
from app.services.ai_tutor_service import AITutorService
from app.services.peer_review_service import PeerReviewService
from app.services.mentorship_service import MentorshipService
from app.services.enterprise_service import EnterpriseService
from app.routers.auth import get_current_user

logger = logging.getLogger(__name__)
security = HTTPBearer()
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, List[str]] = {}
        self.room_connections: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        conn_id = connection_id or f"conn_{user_id}_{datetime.utcnow().timestamp()}"
        
        self.active_connections[conn_id] = websocket
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(conn_id)
        
        logger.info(f"WebSocket connected: {conn_id} for user {user_id}")
        return conn_id
    
    def disconnect(self, connection_id: str, user_id: int = None):
        """Disconnect WebSocket"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id and user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
        
        # Remove from room connections
        for room_id, connections in self.room_connections.items():
            if connection_id in connections:
                connections.remove(connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending message to {connection_id}: {e}")
                        self.disconnect(connection_id, user_id)
    
    async def send_room_message(self, message: dict, room_id: str):
        """Send message to all users in a room"""
        if room_id in self.room_connections:
            disconnected = []
            for connection_id in self.room_connections[room_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending room message to {connection_id}: {e}")
                        disconnected.append(connection_id)
            
            # Clean up disconnected connections
            for conn_id in disconnected:
                self.room_connections[room_id].remove(conn_id)
                # Find user_id and disconnect
                for user_id, connections in self.user_connections.items():
                    if conn_id in connections:
                        self.disconnect(conn_id, user_id)
                        break
    
    async def join_room(self, connection_id: str, room_id: str, user_id: int):
        """Add user to room"""
        if room_id not in self.room_connections:
            self.room_connections[room_id] = []
        
        if connection_id not in self.room_connections[room_id]:
            self.room_connections[room_id].append(connection_id)
        
        # Notify room of new member
        await self.send_room_message({
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }, room_id)
    
    async def leave_room(self, connection_id: str, room_id: str, user_id: int):
        """Remove user from room"""
        if room_id in self.room_connections and connection_id in self.room_connections[room_id]:
            self.room_connections[room_id].remove(connection_id)
            
            # Notify room of member leaving
            await self.send_room_message({
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }, room_id)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/interactive")
async def interactive_learning_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Main WebSocket endpoint for interactive learning features"""
    
    connection_id = None
    user_id = None
    
    try:
        # Authenticate user
        try:
            # For WebSocket auth, we'll accept the token in the query params or headers
            token = websocket.query_params.get("token") or websocket.headers.get("authorization", "").replace("Bearer ", "")
            
            if not token:
                await websocket.close(code=4001, reason="Authentication required")
                return
            
            # Validate token and get user (simplified - in production use proper JWT validation)
            from app.utils.jwt import verify_token
            payload = verify_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                await websocket.close(code=4001, reason="Invalid token")
                return
            
            # Check if user exists
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                await websocket.close(code=4001, reason="User not found")
                return
                
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Accept connection
        connection_id = await manager.connect(websocket, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "code_execution",
                "ai_tutor",
                "peer_review",
                "mentorship",
                "collaboration"
            ]
        })
        
        # Initialize services
        ai_tutor_service = AITutorService(db)
        peer_review_service = PeerReviewService(db)
        mentorship_service = MentorshipService(db)
        enterprise_service = EnterpriseService(db)
        
        # Handle messages
        async for message in websocket.iter_json():
            try:
                message_type = message.get("type")
                
                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == "join_room":
                    room_id = message.get("room_id")
                    if room_id:
                        await manager.join_room(connection_id, room_id, user_id)
                        await websocket.send_json({
                            "type": "room_joined",
                            "room_id": room_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif message_type == "leave_room":
                    room_id = message.get("room_id")
                    if room_id:
                        await manager.leave_room(connection_id, room_id, user_id)
                        await websocket.send_json({
                            "type": "room_left",
                            "room_id": room_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif message_type == "code_execution":
                    await handle_code_execution(message, websocket, user_id, db)
                
                elif message_type == "ai_tutor_chat":
                    await handle_ai_tutor_chat(message, websocket, user_id, ai_tutor_service)
                
                elif message_type == "peer_review":
                    await handle_peer_review(message, websocket, user_id, peer_review_service)
                
                elif message_type == "mentorship":
                    await handle_mentorship(message, websocket, user_id, mentorship_service)
                
                elif message_type == "collaboration":
                    await handle_collaboration(message, websocket, user_id, connection_id)
                
                elif message_type == "enterprise_features":
                    await handle_enterprise_features(message, websocket, user_id, enterprise_service)
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if connection_id and user_id:
            manager.disconnect(connection_id, user_id)

async def handle_code_execution(message: dict, websocket: WebSocket, user_id: int, db: Session):
    """Handle code execution requests"""
    
    try:
        execution_data = message.get("data", {})
        
        # Create execution request
        request = CodeExecutionRequest(
            code=execution_data.get("code", ""),
            language=ExecutionLanguage(execution_data.get("language", "python")),
            lesson_id=execution_data.get("lesson_id"),
            user_id=user_id,
            dependencies=execution_data.get("dependencies", []),
            timeout=execution_data.get("timeout", 30),
            memory_limit=execution_data.get("memory_limit", 256),
            cpu_limit=execution_data.get("cpu_limit", 1.0)
        )
        
        # Execute code
        result = await code_execution_manager.execute_code(request, websocket, db)
        
        # Send completion notification
        await manager.send_personal_message({
            "type": "code_execution_complete",
            "execution_id": result.execution_id,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "execution_time": result.execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)
        
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Code execution failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_ai_tutor_chat(message: dict, websocket: WebSocket, user_id: int, ai_tutor_service: AITutorService):
    """Handle AI tutor chat requests"""
    
    try:
        chat_data = message.get("data", {})
        
        # Get AI tutor response
        response = await ai_tutor_service.handle_tutor_query(
            user_id=user_id,
            question=chat_data.get("question", ""),
            course_id=chat_data.get("course_id"),
            lesson_id=chat_data.get("lesson_id"),
            conversation_id=chat_data.get("conversation_id")
        )
        
        # Send response
        await websocket.send_json({
            "type": "ai_tutor_response",
            "data": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI tutor error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"AI tutor error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_peer_review(message: dict, websocket: WebSocket, user_id: int, peer_review_service: PeerReviewService):
    """Handle peer review requests"""
    
    try:
        review_data = message.get("data", {})
        action = review_data.get("action")
        
        if action == "submit_code":
            # Submit code for review
            result = await peer_review_service.submit_code_for_review(
                user_id=user_id,
                lesson_id=review_data.get("lesson_id"),
                title=review_data.get("title", ""),
                description=review_data.get("description", ""),
                code=review_data.get("code", ""),
                language=review_data.get("language", "python"),
                review_type=review_data.get("review_type", "code_review")
            )
            
            await websocket.send_json({
                "type": "peer_review_submitted",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "submit_feedback":
            # Submit review feedback
            result = await peer_review_service.submit_review_feedback(
                review_request_id=review_data.get("review_request_id"),
                reviewer_id=user_id,
                overall_score=review_data.get("overall_score", 5),
                detailed_feedback=review_data.get("detailed_feedback", {}),
                strengths=review_data.get("strengths", []),
                improvements=review_data.get("improvements", [])
            )
            
            await websocket.send_json({
                "type": "peer_review_feedback_submitted",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "get_reviews":
            # Get reviews for submission
            result = await peer_review_service.get_submission_reviews(
                review_data.get("submission_id")
            )
            
            await websocket.send_json({
                "type": "peer_review_data",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Peer review error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Peer review error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_mentorship(message: dict, websocket: WebSocket, user_id: int, mentorship_service: MentorshipService):
    """Handle mentorship requests"""
    
    try:
        mentorship_data = message.get("data", {})
        action = mentorship_data.get("action")
        
        if action == "find_mentors":
            # Find suitable mentors
            result = await mentorship_service.find_suitable_mentors(
                student_id=user_id,
                expertise_areas=mentorship_data.get("expertise_areas", []),
                session_type=mentorship_data.get("session_type"),
                budget=mentorship_data.get("budget")
            )
            
            await websocket.send_json({
                "type": "mentor_search_results",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "request_session":
            # Request mentorship session
            result = await mentorship_service.request_mentorship(
                student_id=user_id,
                expertise_areas=mentorship_data.get("expertise_areas", []),
                goals=mentorship_data.get("goals", []),
                session_type=mentorship_data.get("session_type"),
                duration_minutes=mentorship_data.get("duration_minutes", 60),
                preferred_mentor_id=mentorship_data.get("mentor_id")
            )
            
            await websocket.send_json({
                "type": "mentorship_requested",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "get_dashboard":
            # Get mentorship dashboard
            dashboard_type = mentorship_data.get("dashboard_type", "mentee")
            
            if dashboard_type == "mentor":
                result = await mentorship_service.get_mentor_dashboard(user_id)
            else:
                result = await mentorship_service.get_mentee_dashboard(user_id)
            
            await websocket.send_json({
                "type": "mentorship_dashboard",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Mentorship error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Mentorship error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_collaboration(message: dict, websocket: WebSocket, user_id: int, connection_id: str):
    """Handle collaborative learning features"""
    
    try:
        collab_data = message.get("data", {})
        action = collab_data.get("action")
        
        if action == "code_collaboration":
            # Real-time code collaboration
            room_id = collab_data.get("room_id")
            if room_id:
                # Broadcast code changes to room
                await manager.send_room_message({
                    "type": "code_change",
                    "user_id": user_id,
                    "changes": collab_data.get("changes", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }, room_id)
        
        elif action == "shared_workspace":
            # Shared workspace collaboration
            room_id = collab_data.get("room_id")
            if room_id:
                await manager.send_room_message({
                    "type": "workspace_update",
                    "user_id": user_id,
                    "workspace_data": collab_data.get("workspace_data", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }, room_id)
        
        elif action == "study_group":
            # Study group features
            study_data = collab_data.get("study_group", {})
            
            if study_data.get("action") == "join":
                room_id = f"study_group_{study_data.get('group_id')}"
                await manager.join_room(connection_id, room_id, user_id)
                await websocket.send_json({
                    "type": "study_group_joined",
                    "group_id": study_data.get("group_id"),
                    "room_id": room_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except Exception as e:
        logger.error(f"Collaboration error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Collaboration error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

async def handle_enterprise_features(message: dict, websocket: WebSocket, user_id: int, enterprise_service: EnterpriseService):
    """Handle enterprise-specific features"""
    
    try:
        enterprise_data = message.get("data", {})
        action = enterprise_data.get("action")
        
        if action == "team_dashboard":
            # Get team dashboard
            team_id = enterprise_data.get("team_id")
            result = await enterprise_service.get_team_dashboard(team_id)
            
            await websocket.send_json({
                "type": "team_dashboard_data",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "enterprise_analytics":
            # Get enterprise analytics
            enterprise_id = enterprise_data.get("enterprise_id")
            period = enterprise_data.get("period", "monthly")
            
            from app.services.enterprise_service import AnalyticsPeriod
            period_enum = AnalyticsPeriod(period)
            
            start_date = datetime.fromisoformat(enterprise_data.get("start_date").replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(enterprise_data.get("end_date").replace('Z', '+00:00'))
            
            result = await enterprise_service.get_enterprise_analytics(
                enterprise_id, period_enum, start_date, end_date
            )
            
            await websocket.send_json({
                "type": "enterprise_analytics_data",
                "data": result,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif action == "custom_curriculum":
            # Handle custom curriculum features
            curriculum_data = enterprise_data.get("curriculum", {})
            
            if curriculum_data.get("action") == "get_builder":
                curriculum_id = curriculum_data.get("curriculum_id")
                result = await enterprise_service.get_curriculum_builder(curriculum_id)
                
                await websocket.send_json({
                    "type": "curriculum_builder_data",
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        elif action == "white_label":
            # Handle white-label features
            wl_data = enterprise_data.get("white_label", {})
            
            if wl_data.get("action") == "get_preview":
                config_id = wl_data.get("config_id")
                result = await enterprise_service.get_white_label_preview(config_id)
                
                await websocket.send_json({
                    "type": "white_label_preview",
                    "data": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    except Exception as e:
        logger.error(f"Enterprise features error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Enterprise features error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })

# Additional WebSocket endpoints for specific features
@router.websocket("/code-execution")
async def code_execution_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Dedicated WebSocket for code execution"""
    await code_execution_manager.handle_websocket_connection(websocket, 0)  # user_id would be extracted from auth

@router.websocket("/ai-tutor")
async def ai_tutor_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Dedicated WebSocket for AI tutor chat"""
    # Simplified AI tutor WebSocket implementation
    await websocket.accept()
    
    ai_tutor_service = AITutorService(db)
    
    try:
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "chat":
                response = await ai_tutor_service.handle_tutor_query(
                    user_id=message.get("user_id", 0),
                    question=message.get("question", ""),
                    course_id=message.get("course_id"),
                    lesson_id=message.get("lesson_id")
                )
                
                await websocket.send_json({
                    "type": "chat_response",
                    "data": response
                })
    
    except WebSocketDisconnect:
        pass

@router.websocket("/peer-review")
async def peer_review_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Dedicated WebSocket for peer review"""
    await websocket.accept()
    
    peer_review_service = PeerReviewService(db)
    
    try:
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "get_dashboard":
                user_id = message.get("user_id", 0)
                result = await peer_review_service.get_reviewer_dashboard(user_id)
                
                await websocket.send_json({
                    "type": "dashboard_data",
                    "data": result
                })
    
    except WebSocketDisconnect:
        pass

@router.websocket("/mentorship")
async def mentorship_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """Dedicated WebSocket for mentorship features"""
    await websocket.accept()
    
    mentorship_service = MentorshipService(db)
    
    try:
        while True:
            message = await websocket.receive_json()
            
            if message.get("type") == "get_dashboard":
                user_id = message.get("user_id", 0)
                dashboard_type = message.get("dashboard_type", "mentee")
                
                if dashboard_type == "mentor":
                    result = await mentorship_service.get_mentor_dashboard(user_id)
                else:
                    result = await mentorship_service.get_mentee_dashboard(user_id)
                
                await websocket.send_json({
                    "type": "dashboard_data",
                    "data": result
                })
    
    except WebSocketDisconnect:
        pass