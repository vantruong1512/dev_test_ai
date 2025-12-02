"""
Facebook Webhook API
POST /webhook/facebook - Receive messages từ Facebook Messenger
GET /webhook/facebook - Verify webhook token
"""

import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any

from core.channel_router import channel_router
from core.facebook_send import send_facebook_message, send_facebook_message_sync, send_facebook_typing
from core.db_service import get_db_service
from core.websocket_service import get_ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/facebook", tags=["facebook"])

# Facebook config từ environment - will be loaded when route is called
def get_facebook_config():
    """Get Facebook config (lazy load to ensure .env is loaded)"""
    return {
        "verify_token": os.getenv("FACEBOOK_VERIFY_TOKEN", ""),
        "app_secret": os.getenv("FACEBOOK_APP_SECRET", "")
    }


def verify_webhook_signature(body: str, x_hub_signature: Optional[str]) -> bool:
    """
    Verify webhook signature từ Facebook
    https://developers.facebook.com/docs/messenger-platform/webhooks
    """
    config = get_facebook_config()
    app_secret = config["app_secret"]
    
    if not x_hub_signature:
        logger.warning("⚠️  Missing x-hub-signature header")
        return False
    
    try:
        # Expected format: sha1=<signature>
        signature_method, signature = x_hub_signature.split("=")
        
        if signature_method != "sha1":
            logger.warning(f"⚠️  Unexpected signature method: {signature_method}")
            return False
        
        # Compute expected signature
        expected_signature = hmac.new(
            app_secret.encode(),
            body.encode(),
            hashlib.sha1
        ).hexdigest()
        
        # Compare signatures
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.error("❌ Invalid webhook signature")
        
        return is_valid
    
    except Exception as e:
        logger.error(f"❌ Signature verification error: {str(e)}")
        return False


@router.get("")
async def verify_facebook_webhook(request: Request):
    """
    GET /webhook/facebook
    Verify webhook endpoint (called by Facebook when configuring webhook)
    Facebook sends: hub.mode, hub.challenge, hub.verify_token (with dots)
    """
    # Get query parameters (FastAPI auto-converts dots to underscores)
    query_params = dict(request.query_params)
    
    # Handle both dot and underscore notation
    mode = query_params.get("hub.mode", "") or query_params.get("hub_mode", "")
    challenge = query_params.get("hub.challenge", "") or query_params.get("hub_challenge", "")
    verify_token_param = query_params.get("hub.verify_token", "") or query_params.get("hub_verify_token", "")
    
    config = get_facebook_config()
    expected_token = config["verify_token"]
    
    logger.info(f"🔍 Facebook webhook verify request")
    logger.info(f"  hub_mode={mode}, hub_verify_token={verify_token_param}")
    logger.info(f"  Expected token: {expected_token}")
    logger.info(f"  Challenge: {challenge}")
    logger.info(f"  Query params: {query_params}")
    
    # Verify mode là "subscribe"
    if mode != "subscribe":
        logger.error(f"❌ Invalid hub_mode: {mode}")
        raise HTTPException(status_code=400, detail="Invalid hub_mode")
    
    # Verify token match
    if verify_token_param != expected_token:
        logger.error(f"❌ Invalid verify token: expected '{expected_token}', got '{verify_token_param}'")
        raise HTTPException(status_code=403, detail="Invalid verify token")
    
    logger.info(f"✅ Webhook verified, returning challenge: {challenge}")
    # Return plain text, not JSON
    return PlainTextResponse(challenge)


async def handle_webhook_event(event: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Xử lý một event từ Facebook webhook
    Event có thể là: message, postback, delivery, read, etc
    """
    logger.info(f"🔔 Processing webhook event: {json.dumps(event)}")
    
    sender = event.get("sender", {})
    psid = sender.get("id")
    
    if not psid:
        logger.warning("⚠️  Missing sender.id in event")
        return
    
    # Tạo session_id dạng fb_<psid>
    session_id = f"fb_{psid}"
    
    # Detect event type từ payload structure
    if "message" in event:
        event_type = "message"
    elif "postback" in event:
        event_type = "postback"
    elif "delivery" in event:
        event_type = "delivery"
    elif "read" in event:
        event_type = "read"
    else:
        event_type = None
    
    logger.info(f"📋 Event type: {event_type}, Session: {session_id}")
    
    # Xử lý message
    if event_type == "message":
        message = event.get("message", {})
        text = message.get("text", "").strip()
        
        if not text:
            logger.info(f"⏭️  Skipping message without text")
            return
        
        logger.info(f"📨 FB message from {psid}: {text}")
        
        # Metadata từ Facebook
        metadata = {
            "psid": psid,
            "mid": message.get("mid"),
            "timestamp": event.get("timestamp"),
            "platform": "facebook"
        }
        
        # 1. Save user message to DB
        try:
            db = get_db_service()
            db.save_chat_message(
                session_id=session_id,
                message=text,
                channel="facebook",
                metadata=json.dumps(metadata)
            )
            logger.info(f"✅ Saved FB message to DB: {session_id}")
        except Exception as e:
            logger.error(f"❌ Error saving message: {str(e)}")
        
        # 2. Broadcast user message to admin
        try:
            ws_manager = get_ws_manager()
            await ws_manager.broadcast_to_admins({
                "type": "new_message",
                "session_id": session_id,
                "channel": "facebook",
                "sender": "user",
                "text": text,
                "timestamp": event.get("timestamp"),
                "psid": psid
            })
            logger.info(f"✅ Broadcasted user message to admin")
        except Exception as e:
            logger.warning(f"⚠️  Could not broadcast: {str(e)}")
        
        # 3. Check chat mode - Nếu HUMAN_ONLINE thì chỉ broadcast, không gọi AI
        db = get_db_service()
        chat_mode = db.get_chat_mode()
        
        if chat_mode == "HUMAN_ONLINE":
            logger.info(f"🙋 Chat mode: HUMAN_ONLINE - Waiting for admin reply, skip AI")
            # Chỉ broadcast message đến admin, không gọi AI
            return
        
        # 4. Process through channel_router (chỉ khi AI_ONLY)
        logger.info(f"🤖 Chat mode: AI_ONLY - Processing with AI")
        try:
            result = await channel_router.process_message(
                session_id=session_id,
                text=text,
                channel="facebook",
                metadata=metadata
            )
            ai_reply = result.get("ai_reply", "Xin lỗi, tôi không thể trả lời lúc này.")
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}")
            ai_reply = "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại."
        
        # 5. Save AI reply to DB
        try:
            db.save_ai_reply(
                session_id=session_id,
                reply_text=ai_reply,
                channel="facebook",
                metadata=json.dumps({"type": "ai_reply", "psid": psid})
            )
            logger.info(f"✅ Saved AI reply to DB")
        except Exception as e:
            logger.error(f"❌ Error saving reply: {str(e)}")
        
        # 6. Broadcast AI reply to admin
        try:
            ws_manager = get_ws_manager()
            await ws_manager.broadcast_to_admins({
                "type": "new_message",
                "session_id": session_id,
                "channel": "facebook",
                "sender": "ai",
                "text": ai_reply,
                "timestamp": int(datetime.now().timestamp() * 1000),
                "psid": psid
            })
            logger.info(f"✅ Broadcasted AI reply to admin")
        except Exception as e:
            logger.warning(f"⚠️  Could not broadcast reply: {str(e)}")
        
        # 7. Send reply via Facebook Send API
        try:
            logger.info(f"📱 Sending FB reply to {psid}...")
            result = await send_facebook_message(psid, ai_reply)
            
            if result.get('success'):
                logger.info(f"✅ FB reply sent successfully: {result.get('message_id')}")
            else:
                logger.error(f"❌ FB reply failed: {result.get('error')}")
        except Exception as fb_error:
            logger.error(f"❌ Error sending FB reply: {fb_error}", exc_info=True)


    
    elif event_type == "postback":
        # Postback từ button click
        postback = event.get("postback", {})
        payload = postback.get("payload", "")
        
        logger.info(f"📌 FB postback from {psid}: {payload}")
        # TODO: Handle postback (menu click, etc)
    
    elif event_type == "delivery":
        # Delivery confirmation
        delivery = event.get("delivery", {})
        logger.info(f"✅ FB delivery confirmation: {delivery}")
    
    elif event_type == "read":
        # Read confirmation
        logger.info(f"👁️  FB read confirmation from {psid}")
    
    else:
        logger.warning(f"⚠️  Unknown FB event type: {event_type}")


@router.post("")
async def receive_facebook_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    POST /webhook/facebook
    Receive messages từ Facebook Messenger
    """
    
    # Lấy raw body để verify signature
    try:
        body = await request.body()
        body_text = body.decode("utf-8")
    except Exception as e:
        logger.error(f"❌ Error reading request body: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid body")
    
    # Verify webhook signature
    x_hub_signature = request.headers.get("x-hub-signature")
    if not verify_webhook_signature(body_text, x_hub_signature):
        logger.error("❌ Webhook signature verification failed")
        raise HTTPException(status_code=403, detail="Signature verification failed")
    
    # Parse JSON
    try:
        payload = json.loads(body_text)
        logger.info(f"📬 Facebook webhook payload: {json.dumps(payload, indent=2)}")
    except Exception as e:
        logger.error(f"❌ Error parsing JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Verify object type
    if payload.get("object") != "page":
        logger.warning(f"⚠️  Invalid object type: {payload.get('object')}")
        raise HTTPException(status_code=400, detail="Invalid object type")
    
    # Xử lý entries
    entries = payload.get("entry", [])
    
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        
        for event in messaging_events:
            # Xử lý event async
            background_tasks.add_task(handle_webhook_event, event, BackgroundTasks())
    
    # Facebook expects 200 OK immediately
    return {"status": "ok"}


# ============================================================================
# Utilities (for testing)
# ============================================================================

async def send_test_message(psid: str, text: str):
    """Helper - gửi test message (only for dev)"""
    logger.info(f"🧪 Sending test message to {psid}: {text}")
    result = await send_facebook_message(psid, text)
    logger.info(f"Result: {result}")
    return result
