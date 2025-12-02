"""
Send Router - Route message tới đúng kênh output (Web WebSocket, Facebook, Zalo, Telegram)
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from core.facebook_send import send_facebook_message
from core.websocket_service import send_to_client

logger = logging.getLogger(__name__)


class Channel(str, Enum):
    """Supported channels"""
    WEB = "web"
    FACEBOOK = "facebook"
    ZALO = "zalo"
    TELEGRAM = "telegram"


class SendRouter:
    """
    Route outgoing messages tới đúng channel
    Hỗ trợ: Web (WebSocket), Facebook, Zalo, Telegram
    """
    
    @staticmethod
    async def send_message(
        session_id: str,
        channel: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message tới user qua channel cụ thể
        
        Args:
            session_id: User session ID (with channel prefix)
            channel: Channel name (web|facebook|zalo|telegram)
            text: Message text
            metadata: Optional metadata (psid, etc)
        
        Returns:
            {
                "success": bool,
                "channel": str,
                "message_id": str or None,
                "error": str or None
            }
        """
        
        logger.info(f"🚀 SendRouter: Sending to {channel} channel")
        
        if channel == Channel.WEB:
            return await SendRouter._send_web(session_id, text, metadata)
        
        elif channel == Channel.FACEBOOK:
            return await SendRouter._send_facebook(session_id, text, metadata)
        
        elif channel == Channel.ZALO:
            return await SendRouter._send_zalo(session_id, text, metadata)
        
        elif channel == Channel.TELEGRAM:
            return await SendRouter._send_telegram(session_id, text, metadata)
        
        else:
            logger.error(f"❌ Unknown channel: {channel}")
            return {
                "success": False,
                "channel": channel,
                "message_id": None,
                "error": f"Unknown channel: {channel}"
            }
    
    @staticmethod
    async def _send_web(
        session_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message qua WebSocket (cho web users)
        """
        
        try:
            # Gửi qua WebSocket tới client
            await send_to_client(
                session_id=session_id,
                message_data={
                    "type": "ai_message",
                    "text": text,
                    "timestamp": metadata.get("timestamp") if metadata else None
                }
            )
            
            logger.info(f"✅ Web message sent to {session_id}")
            
            return {
                "success": True,
                "channel": "web",
                "message_id": session_id,  # WebSocket không có message_id
                "error": None
            }
        
        except Exception as e:
            logger.error(f"❌ Web send error: {str(e)}")
            return {
                "success": False,
                "channel": "web",
                "message_id": None,
                "error": str(e)
            }
    
    @staticmethod
    async def _send_facebook(
        session_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message qua Facebook Send API
        session_id = f"fb_{psid}"
        """
        
        try:
            # Extract PSID từ session_id (fb_<psid>)
            psid = session_id[3:]  # Remove "fb_" prefix
            
            result = await send_facebook_message(
                psid=psid,
                text=text,
                metadata=metadata
            )
            
            if result["success"]:
                logger.info(f"✅ Facebook message sent to {psid}")
            else:
                logger.error(f"❌ Facebook send failed: {result['error']}")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Facebook send exception: {str(e)}")
            return {
                "success": False,
                "channel": "facebook",
                "message_id": None,
                "error": str(e)
            }
    
    @staticmethod
    async def _send_zalo(
        session_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message qua Zalo OA API
        session_id = f"zalo_{user_id}"
        
        TODO: Implement khi có Zalo API integration
        """
        
        logger.warning("⏳ Zalo send not implemented yet")
        
        return {
            "success": False,
            "channel": "zalo",
            "message_id": None,
            "error": "Zalo integration not implemented"
        }
    
    @staticmethod
    async def _send_telegram(
        session_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message qua Telegram Bot API
        session_id = f"tg_{chat_id}"
        
        TODO: Implement khi có Telegram API integration
        """
        
        logger.warning("⏳ Telegram send not implemented yet")
        
        return {
            "success": False,
            "channel": "telegram",
            "message_id": None,
            "error": "Telegram integration not implemented"
        }


# Singleton instance
send_router = SendRouter()


# Convenience functions
async def send_message(
    session_id: str,
    channel: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper function - route message tới channel"""
    return await send_router.send_message(session_id, channel, text, metadata)


async def send_to_channel(
    session_id: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Auto-detect channel từ session_id và gửi message
    
    session_id formats:
    - "uuid" → web channel
    - "fb_psid" → facebook channel
    - "zalo_userid" → zalo channel
    - "tg_chatid" → telegram channel
    """
    
    # Auto-detect channel
    if session_id.startswith("fb_"):
        channel = "facebook"
    elif session_id.startswith("zalo_"):
        channel = "zalo"
    elif session_id.startswith("tg_"):
        channel = "telegram"
    else:
        channel = "web"
    
    return await send_router.send_message(session_id, channel, text, metadata)
