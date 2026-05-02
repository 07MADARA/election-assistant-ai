"""
Main application entry point for the CivicGuide API.
Configures FastAPI, routing, CORS, and rate limiting.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from core.config import get_allowed_origins
from utils.logger import get_logger
from api.routes import router, limiter

load_dotenv()

logger = get_logger(__name__)

app = FastAPI(title="CivicGuide API", description="API for the CivicGuide Election Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure strict CORS securely
allowed_origins = get_allowed_origins()
logger.info(f"Configuring CORS with allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(router, prefix="/api")

# Mount frontend static files
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    async def index_fallback() -> dict:
        """
        Fallback route when the static frontend build is not available.
        """
        logger.info("Serving fallback index route")
        return {"message": "Frontend not built yet. Use API at /api/chat"}

logger.info("CivicGuide API startup complete.")

