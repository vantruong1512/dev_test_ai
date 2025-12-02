"""
Facebook Send Service - Gửi message qua Facebook Send API
https://developers.facebook.com/docs/messenger-platform/reference/send-api
"""

import httpx
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class FacebookSender:
    """
    Gửi message tới Facebook Messenger users
    Yêu cầu: Page Access Token (cấu hình từ env hoặc config)
    """
    
    API_URL = "https://graph.facebook.com/v18.0/me/messages"
    
    def __init__(self, page_access_token: str):
        """
        Args:
            page_access_token: Facebook Page Access Token từ env
        """
        self.page_access_token = page_access_token
        self.http_client = httpx.AsyncClient(timeout=10.0)
        token_preview = page_access_token[-10:] if page_access_token else "EMPTY"
        logger.info(f"✅ FacebookSender initialized with token ending in: {token_preview}")
    
    async def send_text_message(
        self,
        psid: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gửi text message tới Facebook user
        
        Args:
            psid: Facebook Messenger User ID (Page-Scoped User ID)
            text: Message text
            metadata: Optional metadata (message_id, etc)
        
        Returns:
            {
                "success": bool,
                "message_id": str or None,
                "error": str or None
            }
        """
        
        payload = {
            "recipient": {"id": psid},
            "message": {"text": text}
        }
        
        try:
            response = await self.http_client.post(
                self.API_URL,
                json=payload,
                params={"access_token": self.page_access_token}
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("message_id")
                
                logger.info(f"✅ FB message sent to {psid}: {message_id}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "error": None
                }
            else:
                error_text = response.text
                logger.error(f"❌ FB send error: {response.status_code} - {error_text}")
                
                return {
                    "success": False,
                    "message_id": None,
                    "error": f"HTTP {response.status_code}: {error_text}"
                }
        
        except Exception as e:
            logger.error(f"❌ FB send exception: {str(e)}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    async def send_quick_replies(
        self,
        psid: str,
        text: str,
        quick_replies: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gửi message với quick reply buttons
        
        Args:
            psid: Facebook user ID
            text: Message text
            quick_replies: List of {title, payload}
            metadata: Optional metadata
        
        Returns:
            Send result
        """
        
        payload = {
            "recipient": {"id": psid},
            "message": {
                "text": text,
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": reply["title"],
                        "payload": reply.get("payload", reply["title"])
                    }
                    for reply in quick_replies[:10]  # Max 10 replies
                ]
            }
        }
        
        try:
            response = await self.http_client.post(
                self.API_URL,
                json=payload,
                params={"access_token": self.page_access_token}
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("message_id")
                
                logger.info(f"✅ FB quick reply sent to {psid}: {message_id}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "error": None
                }
            else:
                error_text = response.text
                logger.error(f"❌ FB quick reply error: {response.status_code}")
                
                return {
                    "success": False,
                    "message_id": None,
                    "error": f"HTTP {response.status_code}"
                }
        
        except Exception as e:
            logger.error(f"❌ FB quick reply exception: {str(e)}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }
    
    async def send_typing_indicator(self, psid: str) -> bool:
        """
        Gửi "typing..." indicator
        """
        payload = {
            "recipient": {"id": psid},
            "sender_action": "typing_on"
        }
        
        try:
            response = await self.http_client.post(
                self.API_URL,
                json=payload,
                params={"access_token": self.page_access_token}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Typing indicator error: {str(e)}")
            return False
    
    async def close_typing(self, psid: str) -> bool:
        """Tắt "typing..." indicator"""
        payload = {
            "recipient": {"id": psid},
            "sender_action": "typing_off"
        }
        
        try:
            response = await self.http_client.post(
                self.API_URL,
                json=payload,
                params={"access_token": self.page_access_token}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Close typing error: {str(e)}")
            return False
    
    async def mark_seen(self, psid: str) -> bool:
        """Mark message as read"""
        payload = {
            "recipient": {"id": psid},
            "sender_action": "mark_seen"
        }
        
        try:
            response = await self.http_client.post(
                self.API_URL,
                json=payload,
                params={"access_token": self.page_access_token}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Mark seen error: {str(e)}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Initialize từ environment variable
def get_facebook_sender() -> FacebookSender:
    """
    Get Facebook sender instance từ env
    Env var: FACEBOOK_PAGE_ACCESS_TOKEN
    """
    token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    logger.info(f"🔄 get_facebook_sender() called, token exists: {bool(token)}")
    if not token:
        raise ValueError("FACEBOOK_PAGE_ACCESS_TOKEN not set in environment")
    logger.info(f"✅ Creating FacebookSender instance")
    return FacebookSender(token)


# Singleton instance (lazy initialization)
_facebook_sender: Optional[FacebookSender] = None


async def send_facebook_message(
    psid: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Helper function - gửi text message tới Facebook
    """
    global _facebook_sender
    
    if _facebook_sender is None:
        _facebook_sender = get_facebook_sender()
    
    return await _facebook_sender.send_text_message(psid, text, metadata)


async def send_facebook_typing(psid: str) -> bool:
    """Helper - gửi typing indicator"""
    global _facebook_sender
    
    if _facebook_sender is None:
        _facebook_sender = get_facebook_sender()
    
    return await _facebook_sender.send_typing_indicator(psid)


def send_facebook_message_sync(psid: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Sync wrapper for background tasks - gửi message via Facebook Send API
    Handles running in a new thread with its own event loop (for FastAPI BackgroundTasks)
    """
    print(f"\n🔄 [BG SYNC] START - send message to {psid}")  # stdout for visibility
    logger.info(f"🔄 [BG Sync] Starting FB send to {psid}: {text[:50]}...")
    
    try:
        logger.info(f"🔄 [BG Task] Starting FB send to {psid}")
        
        # Create a new event loop for this background task
        # (since background tasks run in a thread pool, not the main loop)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async function
            logger.info(f"🔄 [BG Task] Running async send_facebook_message...")
            result = loop.run_until_complete(send_facebook_message(psid, text, metadata))
            logger.info(f"✅ [BG Task] FB send completed to {psid}: {result}")
            print(f"✅ [BG SYNC] RESULT: {result}")  # stdout
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"❌ [BG Task] Failed to send FB message to {psid}: {str(e)}", exc_info=True)
        print(f"❌ [BG SYNC] ERROR: {e}")  # stdout

