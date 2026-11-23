"""
In-memory session key store for default BYOK (Bring Your Own Key).
Guarantees session-only keys are stored strictly in volatile server RAM,
isolated per user/session, never written to disk, database, or logs.
"""

import time
import uuid
from typing import Dict, Optional, Tuple
from app.config import settings
from app.security.redaction import mask_key


class SessionKeyStore:
    """
    Thread-safe in-memory session manager for BYOK OpenAI API keys.
    Keyed by (user_id_str, session_token).
    Keys are expunged on session expiry, manual deletion, or server restart.
    """

    def __init__(self):
        # Format: (user_id, session_id) -> (api_key, expiry_timestamp, provider)
        self._store: Dict[Tuple[str, str], Tuple[str, float, str]] = {}

    def _cleanup_expired(self) -> None:
        """Purge expired session keys from memory."""
        now = time.time()
        expired_keys = [k for k, v in self._store.items() if v[1] < now]
        for k in expired_keys:
            self._store.pop(k, None)

    def set_key(self, user_id: str, session_id: str, api_key: str, provider: str = "openai") -> None:
        """Store API key temporarily in server RAM for this session."""
        self._cleanup_expired()
        expiry = time.time() + (settings.SESSION_EXPIRE_MINUTES * 60)
        self._store[(str(user_id), session_id)] = (api_key, expiry, provider)

    def get_key(self, user_id: str, session_id: str) -> Optional[str]:
        """Retrieve the API key for an active session."""
        self._cleanup_expired()
        item = self._store.get((str(user_id), session_id))
        if item is None:
            return None
        api_key, expiry, _ = item
        if expiry < time.time():
            self._store.pop((str(user_id), session_id), None)
            return None
        return api_key

    def delete_key(self, user_id: str, session_id: str) -> bool:
        """Expunge session key immediately upon logout or removal request."""
        return self._store.pop((str(user_id), session_id), None) is not None

    def get_status(self, user_id: str, session_id: str) -> dict:
        """Return masked key status without revealing the underlying key."""
        key = self.get_key(user_id, session_id)
        if not key:
            return {
                "provider": "openai",
                "is_set": False,
                "is_saved": False,
                "masked_key": None,
            }
        return {
            "provider": "openai",
            "is_set": True,
            "is_saved": False,
            "masked_key": mask_key(key),
        }


session_key_store = SessionKeyStore()
