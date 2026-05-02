"""
Service module for interacting with the Google Gemini AI.
Provides the GeminiService class which handles message formatting and API calls.
"""
import json
from typing import List
import google.generativeai as genai
from schemas.models import ChatMessage
from core.config import get_gemini_api_key
from utils.logger import get_logger

logger = get_logger(__name__)

# Configure Gemini API using the secure configuration getter
API_KEY = get_gemini_api_key()
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. Gemini integration will fail.")

SYSTEM_INSTRUCTION = (
    "You are CivicGuide, a highly accessible, neutral, and encouraging election process assistant. "
    "Your goal is to explain voter registration, election timelines, and polling processes in simple, "
    "digestible steps. When a user asks a question, first identify their current step in the election "
    "journey (e.g., Unregistered, Registered but confused, Ready to vote). Format your responses using "
    "clear bullet points, short paragraphs, and a reassuring tone. Ask one follow-up question at the end "
    "to guide them to the next step. Do NOT discuss political candidates, parties, or controversial topics. "
    "Maintain strict neutrality. "
    "IMPORTANT: You MUST return a valid JSON object matching the provided schema exactly. "
    "The JSON should contain a single key 'reply' with the response text."
)

class GeminiService:
    """
    Service for managing chat sessions and generating responses using Google Gemini.
    """
    def __init__(self) -> None:
        """
        Initializes the Gemini model with specific instructions and JSON schema constraints.
        """
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "reply": {"type": "STRING"}
                    },
                    "required": ["reply"]
                }
            )
        )

    async def get_chat_response(self, messages: List[ChatMessage]) -> str:
        """
        Sends the chat history and latest message to Gemini and parses the response.
        
        Args:
            messages (List[ChatMessage]): The list of previous and current messages.
            
        Returns:
            str: The plain text reply extracted from the model's JSON response.
            
        Raises:
            Exception: If the Gemini API key is missing or the API call fails.
        """
        if not API_KEY:
            logger.error("Attempted to call Gemini API without an API key configured.")
            raise Exception("Gemini API Key not configured")

        if not messages:
            return "Please provide a valid question."

        history = []
        # Exclude the latest message for the history context
        for msg in messages[:-1]:
            # Pydantic validation ensures msg.role is 'user' or 'model'
            role = msg.role
            text_content = msg.content
            history.append({"role": role, "parts": [{"text": text_content}]})
            
        user_message = messages[-1].content
        
        try:
            logger.info(f"Sending message to Gemini (history length: {len(history)})")
            chat = self.model.start_chat(history=history)
            response = await chat.send_message_async(user_message)
            
            # Parse the JSON string to extract the reply
            response_json = json.loads(response.text)
            return response_json.get("reply", "I'm sorry, I couldn't understand that.")
        except json.JSONDecodeError:
            logger.warning("Gemini failed to return valid JSON, falling back to raw text.", exc_info=True)
            return response.text
        except Exception as e:
            logger.error(f"Failed to communicate with Gemini API: {e}", exc_info=True)
            raise
