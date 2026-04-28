import os
import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from api.routes import router, limiter

load_dotenv()

# Setup Google Cloud structured JSON logging
class GCPJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

logger = logging.getLogger("civicguide")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(GCPJSONFormatter())
logger.addHandler(handler)

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

# Include the API router
app.include_router(router, prefix="/api")

# Mount frontend static files
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    async def index_fallback():
        logger.info("Serving fallback index route")
        return {"message": "Frontend not built yet. Use API at /api/chat"}

logger.info("CivicGuide API startup complete.")
