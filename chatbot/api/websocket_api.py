"""
WebSocket API - Real-time 2-way messaging
User: /ws/chat/{session_id} - Nhận AI reply + Admin reply
Admin: /ws/stream/admin - Nhận tất cả user messages + typing events
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from core.websocket_service import get_ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/stream/admin")
async def admin_stream_websocket(websocket: WebSocket):
    """
    WebSocket cho admin (global stream)
    Admin nhận mọi events: user messages, typing, connections
    """
    ws_manager = get_ws_manager()
    await ws_manager.connect_admin(websocket)
    
    try:
        while True:
            # Nhận messages từ admin
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "typing":
                # Admin typing indicator
                session_id = data.get("session_id")
                is_typing = data.get("is_typing", False)
                await ws_manager.broadcast_typing(session_id, is_typing, from_admin=True)
            
            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "get_stats":
                # Get connection stats
                stats = ws_manager.get_stats()
                await websocket.send_json({
                    "type": "stats",
                    "data": stats
                })
    
    except WebSocketDisconnect:
        ws_manager.disconnect_admin(websocket)
        logger.info("Admin WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"❌ Admin WebSocket error: {e}")
        ws_manager.disconnect_admin(websocket)


@router.websocket("/chat/{session_id}")
async def user_chat_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket cho user (per session)
    User nhận: AI responses, Admin replies, typing indicators
    """
    ws_manager = get_ws_manager()
    await ws_manager.connect_user(session_id, websocket)
    
    try:
        while True:
            # Nhận messages từ user (typing indicator)
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "typing":
                # User typing indicator → broadcast to admins
                is_typing = data.get("is_typing", False)
                await ws_manager.broadcast_typing(session_id, is_typing, from_admin=False)
            
            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        ws_manager.disconnect_user(session_id)
        logger.info(f"User {session_id} WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"❌ User {session_id} WebSocket error: {e}")
        ws_manager.disconnect_user(session_id)
