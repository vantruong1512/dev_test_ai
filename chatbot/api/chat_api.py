"""
Chat API - Endpoints cho chatbot
Tích hợp RAG + LLM với validation và error handling
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

from core.rag_service import get_rag_service
from core.llm_service import get_llm_service
from core.db_service import get_db_service, ChatMode
from core.websocket_service import get_ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# ==================== REQUEST/RESPONSE MODELS ====================

class ChatRequest(BaseModel):
    """Request model cho chat"""
    message: str = Field(..., min_length=1, max_length=1000, description="Tin nhắn của user")
    session_id: str = Field(..., min_length=1, max_length=100, description="Session ID để tracking")
    email: EmailStr = Field(..., description="Email của user (bắt buộc)")
    name: Optional[str] = Field(None, max_length=100, description="Tên của user (optional)")
    phone: Optional[str] = Field(None, max_length=20, description="SĐT của user (optional)")

class ChatResponse(BaseModel):
    """Response model cho chat"""
    reply: str
    session_id: str
    mode: str
    provider: Optional[str] = None
    context_preview: Optional[str] = None  # Preview context để debug

class ErrorResponse(BaseModel):
    """Response model cho lỗi"""
    error: str
    detail: Optional[str] = None

# ==================== ENDPOINTS ====================

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Endpoint chính để chat với bot
    
    Luồng xử lý:
    1. Kiểm tra chat mode (AI_ONLY vs HUMAN_ONLINE)
    2. Nếu AI_ONLY:
       - Load context từ RAG
       - Generate response từ LLM
       - Lưu chat history
    3. Nếu HUMAN_ONLINE:
       - Lưu message để nhân viên xử lý
       - Trả về thông báo chờ
    """
    
    try:
        # ✅ Validate email
        if not request.email or not request.email.strip():
            raise HTTPException(status_code=400, detail="Email là bắt buộc")
        
        # Get services
        db = get_db_service()
        rag = get_rag_service()  # Dùng RAG service (đã có Vector DB inside)
        llm = get_llm_service()
        
        # 1. Kiểm tra/Tạo user - 1 email/phone = 1 user duy nhất
        # save_user_info sẽ tự động merge nếu email/phone đã tồn tại
        try:
            user_id = db.save_user_info(
                session_id=request.session_id,
                name=request.name,
                email=request.email,
                phone=request.phone
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # User đã được save/update với session_id MỚI từ request
        # Không cần lấy canonical session vì backend đã update session_id cho user
        logger.info(f"👤 User ID: {user_id}, Email: {request.email}, Session: {request.session_id}")
        
        # 2. Kiểm tra chat mode
        chat_mode = db.get_chat_mode()
        logger.info(f"🔄 Chat mode hiện tại: {chat_mode.value}")
        
        if chat_mode == ChatMode.HUMAN_ONLINE:
            # 📝 Mode HUMAN_ONLINE: Lưu message, NHƯ chưa gửi → admin trả lời sau
            db.save_chat_to_history(
                user_id=user_id,
                session_id=request.session_id,
                message=request.message,
                reply=None,
                provider="human_pending"
            )
            
            # Giữ lại save vào chat_messages cũ để tương thích
            db.save_chat_message(
                session_id=request.session_id,
                user_message=request.message,
                bot_response=None,
                provider="human_pending"
            )
            
            # 🔔 CHỈ BROADCAST 1 EVENT: new_user_message (để admin thấy)
            ws_manager = get_ws_manager()
            await ws_manager.broadcast_new_message(
                session_id=request.session_id,
                message={
                    "text": request.message,
                    "user_info": {
                        "email": request.email,
                        "name": request.name,
                        "phone": request.phone,
                        "user_id": user_id  # ← Quan trọng: gửi user_id
                    }
                },
                from_admin=False  # ← Chỉ broadcast cho admins, không broadcast cho user
            )
            
            return ChatResponse(
                reply="Tin nhắn của bạn đã được ghi nhận. Nhân viên sẽ phản hồi sớm nhất có thể. Vui lòng chờ trong giây lát! 😊",
                session_id=request.session_id,
                mode="HUMAN_ONLINE",
                provider="human_pending"
            )
        
        # Mode AI_ONLY - xử lý bằng RAG + LLM
        logger.info(f"🤖 Xử lý câu hỏi bằng AI: {request.message}")
        
        # 1. Build context từ Vector RAG (semantic search)
        try:
            context = rag.build_context(request.message, max_chars=3000)
            
            if not context:
                logger.warning("⚠️ Không có context từ tài liệu")
                context = "Không tìm thấy tài liệu liên quan trong hệ thống."
            
            logger.info(f"📚 Context length: {len(context)} chars")
        
        except Exception as e:
            logger.error(f"❌ Lỗi build context: {e}")
            context = "Lỗi đọc tài liệu hệ thống."
        
        # 2. Generate response từ LLM
        try:
            llm_result = await llm.generate_with_context(
                user_question=request.message,
                context=context,
                retry=2
            )
            
            if not llm_result['success']:
                raise Exception(llm_result.get('error', 'Unknown error'))
            
            bot_response = llm_result['answer']
            provider = llm_result['provider']
            
            logger.info(f"✅ LLM response: {len(bot_response)} chars, provider={provider}")
        
        except Exception as e:
            logger.error(f"❌ Lỗi generate LLM: {e}")
            
            # Fallback response
            bot_response = (
                "Xin lỗi, hệ thống AI tạm thời không phản hồi được. "
                "Vui lòng thử lại sau hoặc liên hệ nhân viên hỗ trợ qua email: support@example.com"
            )
            provider = "error_fallback"
        
        # 3. Lưu chat history vào cả 2 bảng
        # Bảng mới (chat_history) - liên kết với user
        db.save_chat_to_history(
            user_id=user_id,
            session_id=request.session_id,
            message=request.message,
            reply=bot_response,
            context_used=context[:500],
            provider=provider
        )
        
        # Bảng cũ (chat_messages) - giữ tương thích
        db.save_chat_message(
            session_id=request.session_id,
            user_message=request.message,
            bot_response=bot_response,
            context_used=context[:500],  # Chỉ lưu preview
            provider=provider
        )
        
        # 4. Trả về response
        context_preview = context[:200] + "..." if len(context) > 200 else context
        
        return ChatResponse(
            reply=bot_response,
            session_id=request.session_id,
            mode="AI_ONLY",
            provider=provider,
            context_preview=context_preview
        )
    
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi hệ thống: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 50):
    """
    Lấy lịch sử chat của một session
    """
    try:
        db = get_db_service()
        history = db.get_chat_history(session_id, limit)
        
        return {
            "session_id": session_id,
            "count": len(history),
            "messages": history
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_all_sessions(limit: int = 100):
    """
    Lấy danh sách tất cả sessions
    """
    try:
        db = get_db_service()
        sessions = db.get_all_sessions(limit)
        
        return {
            "count": len(sessions),
            "sessions": sessions
        }
    
    except Exception as e:
        logger.error(f"❌ Lỗi lấy sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check cho chat service
    """
    try:
        db = get_db_service()
        rag = get_rag_service()
        llm = get_llm_service()
        
        # Test database
        stats = db.get_statistics()
        
        # Test Vector RAG
        rag_stats = rag.get_statistics()
        
        # Test LLM (nếu cần)
        # llm_test = await llm.test_connection()
        
        return {
            "status": "ok",
            "database": {
                "total_messages": stats['total_messages'],
                "total_sessions": stats['total_sessions'],
                "chat_mode": stats['chat_mode']
            },
            "vector_rag": {
                "total_chunks": rag_stats['total_chunks'],
                "chunk_size": rag_stats['chunk_size'],
                "max_context_chars": rag_stats['max_context_chars']
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
