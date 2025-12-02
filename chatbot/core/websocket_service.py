"""
WebSocket Service - Real-time messaging
Admin có 1 connection global nhận tất cả events
User có connection riêng theo session_id
"""
import logging
from typing import Dict, Set
from fastapi import WebSocket
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Quản lý WebSocket connections
    - Admin: 1 connection global nhận tất cả events
    - Users: mỗi session_id có 1 connection riêng
    """
    
    def __init__(self):
        # Admin connections (có thể có nhiều admin tabs)
        self.admin_connections: Set[WebSocket] = set()
        
        # User connections: {session_id: WebSocket}
        self.user_connections: Dict[str, WebSocket] = {}
    
    # ==================== ADMIN CONNECTIONS ====================
    
    async def connect_admin(self, websocket: WebSocket):
        """Connect admin websocket"""
        await websocket.accept()
        self.admin_connections.add(websocket)
        logger.info(f"✅ Admin connected. Total admins: {len(self.admin_connections)}")
        
        # Gửi welcome message
        await websocket.send_json({
            "type": "connected",
            "role": "admin",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to admin channel"
        })
    
    def disconnect_admin(self, websocket: WebSocket):
        """Disconnect admin websocket"""
        self.admin_connections.discard(websocket)
        logger.info(f"❌ Admin disconnected. Total admins: {len(self.admin_connections)}")
    
    async def broadcast_to_admins(self, message: dict):
        """Broadcast message to all admin connections"""
        dead_connections = set()
        
        for connection in self.admin_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ Error sending to admin: {e}")
                dead_connections.add(connection)
        
        # Remove dead connections
        for dead in dead_connections:
            self.admin_connections.discard(dead)
    
    # ==================== USER CONNECTIONS ====================
    
    async def connect_user(self, session_id: str, websocket: WebSocket):
        """Connect user websocket"""
        await websocket.accept()
        
        # Ngắt kết nối cũ nếu có (user mở nhiều tabs)
        if session_id in self.user_connections:
            old_ws = self.user_connections[session_id]
            try:
                await old_ws.close()
            except:
                pass
        
        self.user_connections[session_id] = websocket
        logger.info(f"✅ User connected: {session_id}. Total users: {len(self.user_connections)}")
        
        # Gửi welcome message
        await websocket.send_json({
            "type": "connected",
            "role": "user",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to chat"
        })
        
        # Notify admins về user mới kết nối
        await self.broadcast_to_admins({
            "type": "user_connected",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect_user(self, session_id: str):
        """Disconnect user websocket"""
        if session_id in self.user_connections:
            del self.user_connections[session_id]
            logger.info(f"❌ User disconnected: {session_id}. Total users: {len(self.user_connections)}")
    
    async def send_to_user(self, session_id: str, message: dict):
        """Send message to specific user"""
        if session_id in self.user_connections:
            try:
                await self.user_connections[session_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"❌ Error sending to user {session_id}: {e}")
                self.disconnect_user(session_id)
                return False
        else:
            logger.warning(f"⚠️ User {session_id} not connected")
            return False
    
    # ==================== MESSAGE BROADCASTING ====================
    
    async def broadcast_new_message(self, session_id: str, message: dict, from_admin: bool = False):
        """
        Broadcast message mới
        - Gửi đến user cụ thể
        - Gửi đến tất cả admins
        """
        timestamp = datetime.now().isoformat()
        
        if from_admin:
            # Admin gửi message cho user
            user_msg = {
                "type": "new_message",
                "role": "assistant",
                "text": message.get("text"),
                "timestamp": timestamp,
                "provider": "admin"
            }
            await self.send_to_user(session_id, user_msg)
            
            # Notify all admins
            admin_msg = {
                "type": "message_sent",
                "session_id": session_id,
                "role": "assistant",
                "text": message.get("text"),
                "timestamp": timestamp,
                "provider": "admin"
            }
            await self.broadcast_to_admins(admin_msg)
            
        else:
            # User gửi message
            # Notify all admins về message mới
            admin_msg = {
                "type": "new_user_message",
                "session_id": session_id,
                "role": "user",
                "text": message.get("text"),
                "timestamp": timestamp,
                "user_info": message.get("user_info", {})
            }
            await self.broadcast_to_admins(admin_msg)
    
    async def broadcast_typing(self, session_id: str, is_typing: bool, from_admin: bool = False):
        """Broadcast typing indicator"""
        if from_admin:
            # Admin đang typing → notify user
            await self.send_to_user(session_id, {
                "type": "typing",
                "is_typing": is_typing,
                "role": "admin"
            })
        else:
            # User đang typing → notify admins
            await self.broadcast_to_admins({
                "type": "user_typing",
                "session_id": session_id,
                "is_typing": is_typing
            })
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "admin_connections": len(self.admin_connections),
            "user_connections": len(self.user_connections),
            "active_sessions": list(self.user_connections.keys())
        }


# Singleton instance
_ws_manager = None

def get_ws_manager() -> WebSocketManager:
    """Get WebSocket manager instance (singleton)"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
        logger.info("✅ WebSocket Manager initialized")
    return _ws_manager
