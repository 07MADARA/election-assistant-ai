import os
from typing import List

def get_allowed_origins() -> List[str]:
    """
    Retrieve allowed CORS origins from the environment variable.
    Defaults to localhost for development if not provided.
    
    Returns:
        List[str]: A list of allowed origin URLs.
    """
    origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173")
    return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

def get_gemini_api_key() -> str | None:
    """
    Retrieve the Google Gemini API Key from the environment.
    
    Returns:
        str | None: The API key if set, else None.
    """
    return os.environ.get("GEMINI_API_KEY")
