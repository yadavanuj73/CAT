"""
Rate limiting helpers.
Provides in-memory rate limiting when slowapi or redis is used.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
