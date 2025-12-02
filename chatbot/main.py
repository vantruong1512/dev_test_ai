"""
Main FastAPI Application - Chatbot AI RAG
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv(".env.local", override=True)

from api.chat_api import router as chat_router
from api.admin_api import router as admin_router
from api.websocket_api import router as websocket_router
from api.facebook_webhook import router as facebook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chatbot AI RAG",
    description="Hệ thống chatbot đa kênh với RAG và LLM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers BEFORE mounting static files
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(websocket_router)
app.include_router(facebook_router)

# Add API endpoints BEFORE static files
@app.get("/api/config")
async def get_config():
    """Get frontend configuration"""
    return {
        "api_base": os.getenv("API_BASE_URL", "http://localhost:8000"),
        "version": "1.0.0"
    }

@app.get("/api")
async def api_root():
    """Root endpoint"""
    return {
        "app": "Chatbot AI RAG",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat/message",
            "health": "/api/chat/health",
            "admin": "/api/admin/statistics",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Chatbot AI RAG is running"
    }

# Serve static files từ frontend/dist AFTER API routes
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
    logger.info(f"✅ Static files mounted from: {frontend_dist}")
else:
    logger.warning(f"⚠️  Frontend dist folder not found: {frontend_dist}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Chatbot AI RAG server...")
    logger.info("📚 Docs available at: http://localhost:8000/docs")
    
    # Disable reload on Windows to avoid multiprocessing issues with torch
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable auto-reload for Windows compatibility
        log_level="info"
    )
