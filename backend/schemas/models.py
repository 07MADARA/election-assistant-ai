"""
Pydantic schemas for the CivicGuide API requests and responses.
Provides strict validation to prevent malicious payloads or API abuse.
"""
from typing import List, Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Schema representing a single message in the chat history."""
    role: Literal["user", "model"] = Field(
        ..., 
        description="The role of the message sender. Must be 'user' or 'model'."
    )
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=1000, 
        description="The text content of the message. Max length is 1000 characters."
    )

class ChatRequest(BaseModel):
    """Schema for the incoming chat request containing message history."""
    messages: List[ChatMessage] = Field(
        ..., 
        min_length=1, 
        max_length=20, 
        description="The list of chat messages. Must contain between 1 and 20 messages."
    )

class ChatResponse(BaseModel):
    """Schema for the response sent back to the client."""
    reply: str = Field(
        ..., 
        description="The AI-generated reply."
    )
