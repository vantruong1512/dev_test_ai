"""
Admin API - Quản lý tài liệu, settings, users
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime

from core.db_service import get_db_service, ChatMode
from core.rag_service import get_rag_service
from core.websocket_service import get_ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== REQUEST/RESPONSE MODELS ====================

class SetChatModeRequest(BaseModel):
    """Request để đổi chat mode"""
    mode: ChatMode

class DocumentInfo(BaseModel):
    """Thông tin document"""
    filename: str
    file_size: int
    char_count: int
    extension: str
    uploaded_at: str

# ==================== SETTINGS ENDPOINTS ====================

@router.get("/settings/chat-mode")
async def get_chat_mode():
    """
    Lấy chế độ chat hiện tại
    """
    try:
        db = get_db_service()
        mode = db.get_chat_mode()
        
        return {
            "mode": mode.value,
            "description": "AI_ONLY: AI trả lời tự động | HUMAN_ONLINE: Nhân viên trả lời"
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy chat mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/chat-mode")
async def set_chat_mode(request: SetChatModeRequest):
    """
    Đổi chế độ chat (Admin only)
    
    Args:
        mode: AI_ONLY hoặc HUMAN_ONLINE
    """
    try:
        db = get_db_service()
        db.set_chat_mode(request.mode)
        
        logger.info(f"⚙️ Đổi chat mode -> {request.mode.value}")
        
        return {
            "success": True,
            "mode": request.mode.value,
            "message": f"Đã chuyển sang chế độ {request.mode.value}"
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi đổi chat mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCUMENT MANAGEMENT ====================

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload tài liệu huấn luyện RAG
    
    Hỗ trợ: .txt, .md, .pdf, .docx (Word 2007+)
    Không hỗ trợ: .doc (Word 97-2003) - Vui lòng chuyển sang .docx
    """
    try:
        rag = get_rag_service()
        db = get_db_service()
        
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in rag.supported_extensions:
            error_msg = f"File không được hỗ trợ. Chỉ chấp nhận: {', '.join(rag.supported_extensions)}"
            if file_ext == '.doc':
                error_msg += "\n\n💡 File .doc (Word 97-2003) không được hỗ trợ.\nVui lòng mở file trong Microsoft Word và Save As → chọn định dạng .docx (Word 2007+)"
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        # Save file to uploads directory
        upload_path = rag.uploads_dir / file.filename
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📤 Upload file: {file.filename} -> {upload_path}")
        
        # Load file để lấy metadata
        doc_info = rag.load_single_file(upload_path)
        
        if not doc_info:
            raise HTTPException(status_code=400, detail="Không thể đọc file")
        
        # Lưu metadata vào database
        db.save_document_metadata(
            filename=doc_info['filename'],
            file_path=str(upload_path),
            file_size=doc_info['size'],
            char_count=doc_info['char_count'],
            extension=doc_info['extension']
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "size": doc_info['size'],
            "char_count": doc_info['char_count'],
            "message": f"Upload thành công: {file.filename}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[DocumentInfo])
async def get_all_documents():
    """
    Lấy danh sách tất cả tài liệu
    """
    try:
        db = get_db_service()
        documents = db.get_all_documents()
        
        return documents
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Xóa tài liệu
    """
    try:
        rag = get_rag_service()
        db = get_db_service()
        
        # Xóa file vật lý
        file_path = rag.uploads_dir / filename
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"🗑️ Xóa file: {file_path}")
        
        # Xóa metadata trong DB
        db.delete_document(filename)
        
        return {
            "success": True,
            "message": f"Đã xóa: {filename}"
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi xóa document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/stats")
async def get_document_stats():
    """
    Thống kê tài liệu
    """
    try:
        rag = get_rag_service()
        stats = rag.get_document_stats()
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USER MANAGEMENT ====================

@router.get("/users")
async def get_all_users(limit: int = 100):
    """
    Lấy danh sách tất cả users (leads)
    """
    try:
        db = get_db_service()
        users = db.get_all_users(limit)
        
        return {
            "count": len(users),
            "users": users
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{session_id}")
async def get_user_info(session_id: str):
    """
    Lấy thông tin một user
    Support cả web users (users table) và multi-channel (chat_messages)
    """
    try:
        db = get_db_service()
        
        # Check if multi-channel session
        is_multi_channel = (
            session_id.startswith('fb_') or 
            session_id.startswith('zalo_') or 
            session_id.startswith('tg_')
        )
        
        if is_multi_channel:
            # For multi-channel, get info from chat_messages
            messages = db.get_chat_history(session_id, limit=1)
            if not messages:
                raise HTTPException(status_code=404, detail="Session không tồn tại")
            
            # Extract channel
            channel = messages[0].get('channel', 'unknown')
            if session_id.startswith('fb_'):
                channel = 'facebook'
            elif session_id.startswith('zalo_'):
                channel = 'zalo'
            elif session_id.startswith('tg_'):
                channel = 'telegram'
            
            # Return basic info for multi-channel users
            return {
                "session_id": session_id,
                "channel": channel,
                "email": None,
                "name": None,
                "phone": None,
                "created_at": messages[0].get('created_at')
            }
        else:
            # For web users, get from users table
            user = db.get_user_info(session_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="User không tồn tại")
            
            return user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi lấy user info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CHAT HISTORY ====================

@router.get("/users/{session_id}/history")
async def get_user_history_by_session(session_id: str, limit: int = 50):
    """
    Lấy lịch sử chat của user theo session_id
    Support cả web (chat_history) và multi-channel (chat_messages)
    """
    try:
        db = get_db_service()
        
        # Kiểm tra xem session có từ multi-channel (fb_*, zalo_*, etc)
        if session_id.startswith('fb_') or session_id.startswith('zalo_') or session_id.startswith('tg_'):
            # Lấy từ chat_messages table (multi-channel)
            logger.info(f"📋 Lấy history từ chat_messages: session={session_id}")
            
            messages = db.get_chat_history(session_id, limit=limit)
            
            # Transform để match frontend format
            result = []
            for msg in messages:
                sender = msg.get('sender', 'unknown')
                text = msg.get('text', '')
                ts = msg.get('created_at')
                
                result.append({
                    "role": "user" if sender == "user" else "assistant",
                    "text": text,
                    "ts": ts,
                    "sender": sender,
                    "channel": msg.get('channel', 'unknown')
                })
            
            return {"history": result}
        else:
            # Lấy từ chat_history table (web) - original flow
            user = db.get_user_info(session_id)
            if not user:
                raise HTTPException(status_code=404, detail="User không tồn tại")
            
            user_id = user['id']
            logger.info(f"📋 Lấy history: session={session_id} → user_id={user_id}")
            
            # Lấy từ chat_history table
            cursor = db.conn.cursor()
            cursor.execute("""
                SELECT * FROM chat_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            history_raw = cursor.fetchall()
            history_raw = [dict(row) for row in history_raw]
            
            # Transform data
            messages = []
            for msg in history_raw:
                if msg.get('message') and msg.get('message').strip():
                    messages.append({
                        "role": "user",
                        "text": msg.get('message'),
                        "ts": msg.get('created_at')
                    })
                if msg.get('reply') and msg.get('reply').strip():
                    messages.append({
                        "role": "assistant",
                        "text": msg.get('reply'),
                        "ts": msg.get('created_at'),
                        "provider": msg.get('provider')
                    })
            
            return {"history": messages}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi lấy history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/email/{email}/history")
async def get_user_history_by_email(email: str, limit: int = 50):
    """
    Lấy lịch sử chat theo email
    """
    try:
        db = get_db_service()
        
        # Kiểm tra user tồn tại
        user = db.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail=f"User với email {email} không tồn tại")
        
        # Lấy lịch sử chat
        history = db.get_chat_history_by_email(email, limit)
        
        return {
            "email": email,
            "user": {
                "session_id": user.get('session_id'),
                "name": user.get('name'),
                "phone": user.get('phone')
            },
            "count": len(history),
            "history": history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi lấy chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN LIVE CHAT ====================

class AdminMessageRequest(BaseModel):
    """Request để admin gửi message"""
    session_id: str
    message: str
    role: str = "assistant"  # assistant (admin reply) hoặc system

@router.post("/reply")
async def admin_reply_to_user(request: AdminMessageRequest):
    """
    Admin trả lời user qua WebSocket + DB
    Support cả web sessions và multi-channel (Facebook, Zalo, etc)
    
    🔔 QUAN TRỌNG: Chỉ broadcast 1 EVENT duy nhất - "message_sent"
    Không broadcast 2 lần hoặc 2 loại event.
    """
    try:
        db = get_db_service()
        
        # B1: Kiểm tra session tồn tại
        # Phân biệt multi-channel (fb_, zalo_) vs web session
        is_multi_channel = (
            request.session_id.startswith('fb_') or 
            request.session_id.startswith('zalo_') or 
            request.session_id.startswith('tg_')
        )
        
        if is_multi_channel:
            # Multi-channel: kiểm tra có messages trong chat_messages
            messages = db.get_chat_history(request.session_id, limit=1)
            if not messages:
                raise HTTPException(status_code=404, detail="Session không tồn tại")
            
            logger.info(f"💬 [ADMIN REPLY - MULTI-CHANNEL] session={request.session_id}, msg={request.message[:50]}...")
            
            # Lưu vào chat_messages (multi-channel)
            db.save_ai_reply(
                session_id=request.session_id,
                reply_text=request.message,
                channel=messages[0].get('channel', 'unknown'),
                metadata=json.dumps({"provider": "admin", "type": "admin_reply"})
            )
            logger.info(f"✅ Lưu vào chat_messages (multi-channel)")
            
        else:
            # Web session: kiểm tra trong users table
            user = db.get_user_info(request.session_id)
            if not user:
                raise HTTPException(status_code=404, detail="Session không tồn tại")
            
            user_id = user['id']
            logger.info(f"💬 [ADMIN REPLY - WEB] session={request.session_id}, user_id={user_id}, msg={request.message[:50]}...")
            
            # Lưu vào DB (chat_history + chat_messages)
            db.save_chat_to_history(
                user_id=user_id,
                session_id=request.session_id,
                message="",
                reply=request.message,
                provider="admin"
            )
            logger.info(f"✅ Lưu vào chat_history")
            
            db.save_chat_message(
                session_id=request.session_id,
                user_message="",
                bot_response=request.message,
                provider="admin"
            )
            logger.info(f"✅ Lưu vào chat_messages")
        
        # B2: Broadcast WebSocket - CHỈ 1 EVENT DUY NHẤT
        ws_manager = get_ws_manager()
        
        # 🔔 Event 1: Gửi cho USER qua user's WebSocket
        # Tên event: "new_message" (user nhận tin nhắn từ admin)
        await ws_manager.send_to_user(request.session_id, {
            "type": "new_message",
            "role": "assistant",
            "text": request.message,
            "timestamp": datetime.now().isoformat(),
            "provider": "admin"
        })
        logger.info(f"📤 Gửi event cho USER")
        
        # 🔔 Event 2: Gửi cho ADMINS qua admin's WebSocket
        # Tên event: "message_sent" (admin khác thấy tin nhắn vừa gửi)
        await ws_manager.broadcast_to_admins({
            "type": "message_sent",
            "session_id": request.session_id,
            "role": "assistant",
            "text": request.message,
            "timestamp": datetime.now().isoformat(),
            "provider": "admin"
        })
        logger.info(f"📤 Gửi event cho ADMINS")
        
        # B3: Nếu là Facebook session, gửi qua Facebook Send API
        if is_multi_channel and request.session_id.startswith('fb_'):
            try:
                from core.facebook_send import send_facebook_message
                psid = request.session_id.replace('fb_', '')
                logger.info(f"📱 Gửi admin reply về Facebook: {psid}")
                
                result = await send_facebook_message(psid, request.message)
                if result.get('success'):
                    logger.info(f"✅ Gửi Facebook thành công: {result.get('message_id')}")
                else:
                    logger.error(f"❌ Facebook send failed: {result.get('error')}")
            except Exception as fb_error:
                logger.error(f"❌ Lỗi gửi Facebook: {fb_error}", exc_info=True)
        
        logger.info(f"✅ [ADMIN REPLY SUCCESS] Gửi xong tin nhắn")
        
        return {
            "success": True,
            "message": "Reply sent",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error admin reply: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/active-sessions")
async def get_active_sessions():
    """
    Lấy danh sách sessions đang chờ phản hồi (bao gồm web + multi-channel)
    """
    try:
        db = get_db_service()
        
        # Lấy tất cả sessions từ chat_messages (bao gồm Facebook, web, etc)
        sessions = db.get_all_sessions(limit=100)
        
        active_sessions = []
        for session_info in sessions:
            session_id = session_info['session_id']
            
            # Lấy lịch sử chat từ chat_messages
            messages = db.get_chat_history(session_id, limit=50)
            
            if not messages:
                continue
            
            # Lấy thông tin user nếu có
            user = db.get_user_info(session_id)
            
            # Sort messages by created_at DESC để lấy message mới nhất
            sorted_msgs = sorted(messages, key=lambda x: x.get('created_at', ''), reverse=True)
            last_msg = sorted_msgs[0]
            
            # Kiểm tra nếu message cuối cùng từ user (không phải AI)
            is_user_message = last_msg.get('sender') == 'user'
            
            if is_user_message:
                # Extract channel từ session_id hoặc metadata
                channel = session_info.get('channel', 'unknown')
                if session_id.startswith('fb_'):
                    channel = 'facebook'
                elif session_id.startswith('zalo_'):
                    channel = 'zalo'
                elif session_id.startswith('tg_'):
                    channel = 'telegram'
                
                active_sessions.append({
                    'session_id': session_id,
                    'channel': channel,
                    'email': user.get('email') if user else None,
                    'name': user.get('name') if user else None,
                    'phone': user.get('phone') if user else None,
                    'message_count': session_info.get('message_count', 0),
                    'last_message': last_msg.get('created_at'),
                    'last_text': last_msg.get('text', ''),
                    'waiting_since': last_msg.get('created_at'),
                    'status': 'waiting'
                })
        
        logger.info(f"📋 Active sessions: {len(active_sessions)}")
        return active_sessions
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/send")
async def send_admin_message(request: AdminMessageRequest):
    """
    Admin gửi message trả lời user
    """
    try:
        db = get_db_service()
        
        # Kiểm tra user tồn tại
        user = db.get_user_info(request.session_id)
        if not user:
            raise HTTPException(status_code=404, detail="Session không tồn tại")
        
        # Lưu message từ admin vào history
        # Lưu như một message mới với empty user message và admin reply
        db.save_chat_to_history(
            user_id=user['id'],
            session_id=request.session_id,
            message="",  # Empty user message for admin-initiated messages
            reply=request.message,
            provider="admin"
        )
        
        # Cũng lưu vào bảng cũ để tương thích
        db.save_chat_message(
            session_id=request.session_id,
            user_message="",  # Empty for admin messages
            bot_response=request.message,
            provider="admin"
        )
        
        # Broadcast message to user via WebSocket
        ws_manager = get_ws_manager()
        await ws_manager.broadcast_new_message(
            session_id=request.session_id,
            message={"text": request.message},
            from_admin=True
        )
        
        logger.info(f"💬 Admin sent message to session: {request.session_id}")
        
        return {
            "success": True,
            "message": {
                "role": request.role,
                "text": request.message,
                "ts": db.get_current_timestamp(),
                "sent_by": "admin"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi gửi admin message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/sessions/{session_id}/respond")
async def mark_session_responded(session_id: str):
    """
    Đánh dấu session đã được admin phản hồi
    """
    try:
        db = get_db_service()
        
        # Kiểm tra session tồn tại
        user = db.get_user_info(session_id)
        if not user:
            raise HTTPException(status_code=404, detail="Session không tồn tại")
        
        logger.info(f"✅ Marked session as responded: {session_id}")
        
        return {
            "session_id": session_id,
            "status": "responded",
            "responded_at": db.get_current_timestamp()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi mark responded: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATISTICS ====================

@router.get("/statistics")
async def get_statistics():
    """
    Thống kê tổng quan hệ thống
    """
    try:
        db = get_db_service()
        stats = db.get_statistics()
        
        return stats
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
