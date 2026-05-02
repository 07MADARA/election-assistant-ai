"""
API routes for the CivicGuide application.
Provides endpoints for health checks and AI chat interaction.
"""
from fastapi import APIRouter, Request, HTTPException
from schemas.models import ChatRequest, ChatResponse
from services.gemini_service import GeminiService
from slowapi import Limiter
from slowapi.util import get_remote_address
from async_lru import alru_cache
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
gemini_service = GeminiService()

@alru_cache(maxsize=128)
async def cached_health_check() -> dict:
    """
    Cached health check to demonstrate alru_cache usage.
    
    Returns:
        dict: A dictionary indicating the service status.
    """
    return {"status": "ok", "cached": True}

@router.get("/health", response_model=dict, tags=["Monitoring"])
async def health_check() -> dict:
    """
    Health check endpoint for testing and monitoring.
    
    Returns:
        dict: The health status of the API.
    """
    return await cached_health_check()

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, payload: ChatRequest) -> ChatResponse:
    """
    Handles chat messages and interacts with the Google Gemini API.
    
    Args:
        request (Request): The incoming HTTP request (used by rate limiter).
        payload (ChatRequest): The validated chat request payload.
        
    Returns:
        ChatResponse: The validated response containing the AI's reply.
        
    Raises:
        HTTPException: 500 error if the AI service fails.
    """
    try:
        reply = await gemini_service.get_chat_response(payload.messages)
        return ChatResponse(reply=reply)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate response")
