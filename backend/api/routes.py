from fastapi import APIRouter, Request, HTTPException
from schemas.models import ChatRequest, ChatResponse
from services.gemini_service import GeminiService
from slowapi import Limiter
from slowapi.util import get_remote_address
from async_lru import alru_cache

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
gemini_service = GeminiService()

@alru_cache(maxsize=128)
async def cached_health_check() -> dict:
    """Cached health check to demonstrate alru_cache usage."""
    return {"status": "ok", "cached": True}

@router.get("/health")
async def health_check():
    """Health check endpoint for testing and monitoring."""
    return await cached_health_check()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Handles chat messages and interacts with the Google Gemini API.
    """
    try:
        reply = await gemini_service.get_chat_response(payload.messages)
        return ChatResponse(reply=reply)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")
