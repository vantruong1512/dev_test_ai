"""
Channel Router - Normalize messages từ tất cả kênh (web, facebook, zalo, telegram)
Detect channel, extract metadata, process RAG, route đến send_router
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from core.rag_service import get_rag_service
from core.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class ChannelRouter:
    """
    Normalize messages từ tất cả kênh:
    - web: session_id = UUID
    - facebook: session_id = f"fb_{psid}"
    - zalo: session_id = f"zalo_{user_id}"
    - telegram: session_id = f"tg_{chat_id}"
    """
    
    @staticmethod
    def detect_channel(session_id: str) -> str:
        """Detect channel từ session_id prefix"""
        if session_id.startswith("fb_"):
            return "facebook"
        elif session_id.startswith("zalo_"):
            return "zalo"
        elif session_id.startswith("tg_"):
            return "telegram"
        else:
            return "web"
    
    @staticmethod
    def extract_platform_id(session_id: str, channel: str) -> Optional[str]:
        """Extract platform-specific ID từ session_id"""
        if channel == "facebook" and session_id.startswith("fb_"):
            return session_id[3:]  # Remove "fb_" prefix
        elif channel == "zalo" and session_id.startswith("zalo_"):
            return session_id[5:]  # Remove "zalo_" prefix
        elif channel == "telegram" and session_id.startswith("tg_"):
            return session_id[3:]  # Remove "tg_" prefix
        return None
    
    @staticmethod
    async def process_message(
        session_id: str,
        text: str,
        channel: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main method - xử lý message từ bất kỳ kênh nào
        
        Args:
            session_id: Unique session identifier (with channel prefix)
            text: Message text từ user
            channel: Optional channel name (auto-detect nếu không có)
            metadata: Optional metadata từ kênh (psid, zalo_user_id, etc)
        
        Returns:
            {
                "session_id": str,
                "channel": str,
                "ai_reply": str,
                "metadata": dict
            }
        """
        
        # Auto-detect channel nếu không có
        if channel is None:
            channel = ChannelRouter.detect_channel(session_id)
        
        # Khởi tạo metadata
        if metadata is None:
            metadata = {}
        
        logger.info(f"📨 Processing message from {channel} channel: {text[:50]}...")
        
        # Process through RAG pipeline
        try:
            rag = get_rag_service()
            llm = get_llm_service()
            
            # 1. Retrieve relevant documents
            docs = rag.search_relevant_chunks(text, top_k=3)
            context = "\n\n".join([doc["text"] for doc in docs]) if docs else ""
            
            logger.info(f"📚 Retrieved {len(docs)} documents for context")
            
            # Debug: Log retrieved chunks
            if docs:
                for i, doc in enumerate(docs, 1):
                    logger.info(f"📄 Chunk {i}: {doc['text'][:200]}... (distance: {doc.get('distance', 'N/A')})")
            
            logger.info(f"📝 Context length: {len(context)} chars")
            
            # 2. Generate AI reply with context
            if context:
                result = await llm.generate_with_context(
                    user_question=text,
                    context=context
                )
                ai_reply = result.get('answer', 'Xin lỗi, tôi không thể trả lời lúc này.')
            else:
                # Không có context, trả lời thân thiện
                prompt = f"""Người dùng hỏi: {text}

Hãy trả lời một cách thân thiện. Nếu bạn không có thông tin, hãy nói rõ và gợi ý họ hỏi về các chủ đề bạn có thể giúp."""
                ai_reply = await llm.generate_ollama(prompt)
                if not ai_reply:
                    ai_reply = "Xin lỗi, tôi không thể trả lời lúc này. Vui lòng thử lại sau."
            
            logger.info(f"✅ AI reply generated: {ai_reply[:50]}...")
            
        except Exception as e:
            logger.error(f"❌ Error in RAG pipeline: {e}", exc_info=True)
            ai_reply = "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau."
        
        return {
            "session_id": session_id,
            "channel": channel,
            "ai_reply": ai_reply,
            "metadata": metadata
        }
    
    @staticmethod
    async def get_channel_info(session_id: str) -> Dict[str, Any]:
        """Lấy thông tin user theo session_id"""
        channel = ChannelRouter.detect_channel(session_id)
        platform_id = ChannelRouter.extract_platform_id(session_id, channel)
        
        return {
            "session_id": session_id,
            "channel": channel,
            "platform_id": platform_id
        }


# Singleton instance
channel_router = ChannelRouter()
