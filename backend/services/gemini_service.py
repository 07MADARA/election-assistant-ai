import os
import google.generativeai as genai
from schemas.models import ChatMessage
import json

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

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
    def __init__(self):
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

    async def get_chat_response(self, messages: list[ChatMessage]) -> str:
        if not API_KEY:
            raise Exception("Gemini API Key not configured")

        history = []
        for msg in messages[:-1]:
            role = "user" if msg.role == "user" else "model"
            # Format model text responses back to raw text for history, since it expects text or specific formats
            # The prompt is expecting a JSON return but history can be raw text parts if we strip JSON manually, 
            # but to be safe we'll keep history as text
            text_content = msg.content
            # If msg was previously JSON structured, the frontend already parsed it, so msg.content is pure text
            history.append({"role": role, "parts": [{"text": text_content}]})
            
        user_message = messages[-1].content
        
        chat = self.model.start_chat(history=history)
        response = await chat.send_message_async(user_message)
        
        try:
            # Parse the JSON string to extract the reply
            response_json = json.loads(response.text)
            return response_json.get("reply", "I'm sorry, I couldn't understand that.")
        except json.JSONDecodeError:
            # Fallback if the model ignores the instruction (rare with structured outputs)
            return response.text
