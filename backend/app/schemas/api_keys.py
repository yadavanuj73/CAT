"""
API Key BYOK Schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SessionApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=16, description="AI API key (e.g., Google Gemini AIza... or OpenAI sk-...)")
    provider: str = Field(default="gemini", description="AI Provider (default: gemini)")


class SaveApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=16, description="AI API key to encrypt with AES-256-GCM")
    provider: str = Field(default="gemini", description="AI Provider (default: gemini)")


class ApiKeyStatusResponse(BaseModel):
    provider: str
    is_set: bool
    is_saved: bool
    masked_key: Optional[str] = None
