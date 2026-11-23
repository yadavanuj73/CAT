"""
API Key BYOK Schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SessionApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=20, description="OpenAI API key (e.g., sk-...)")
    provider: str = Field(default="openai", description="AI Provider")


class SaveApiKeyRequest(BaseModel):
    api_key: str = Field(..., min_length=20, description="OpenAI API key to encrypt with AES-256-GCM")
    provider: str = Field(default="openai", description="AI Provider")


class ApiKeyStatusResponse(BaseModel):
    provider: str
    is_set: bool
    is_saved: bool
    masked_key: Optional[str] = None
