import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CivicGuide API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict to actual frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set.")

# Define prompt constraint
SYSTEM_INSTRUCTION = (
    "You are CivicGuide, a highly accessible, neutral, and encouraging election process assistant. "
    "Your goal is to explain voter registration, election timelines, and polling processes in simple, "
    "digestible steps. When a user asks a question, first identify their current step in the election "
    "journey (e.g., Unregistered, Registered but confused, Ready to vote). Format your responses using "
    "clear bullet points, short paragraphs, and a reassuring tone. Ask one follow-up question at the end "
    "to guide them to the next step. Do NOT discuss political candidates, parties, or controversial topics. "
    "Maintain strict neutrality."
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

class ChatResponse(BaseModel):
    reply: str

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Handles chat messages and interacts with the Google Gemini API.
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")

    try:
        # Convert messages to Gemini format
        history = []
        for msg in payload.messages[:-1]: # All but the last message
            role = "user" if msg.role == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg.content}]})

        user_message = payload.messages[-1].content
        
        # Initialize model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Start chat with history
        chat = model.start_chat(history=history)
        
        # Send message (async)
        response = await chat.send_message_async(user_message)
        
        return ChatResponse(reply=response.text)

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

@app.get("/api/health")
async def health_check():
    """Health check endpoint for testing and monitoring."""
    return {"status": "ok"}

# Mount frontend static files
# In development, this might not exist. In production (Docker), it will.
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    async def index_fallback():
        return {"message": "Frontend not built yet. Use API at /api/chat"}
