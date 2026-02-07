from fastapi import Depends, Header, HTTPException
from supabase import create_client, Client

from config.settings import settings
from database.db_manager import DBManager


# Singleton for read-only API client (uses anon key for RLS enforcement)
_api_client: Client | None = None


def get_api_client() -> Client:
    """Return a Supabase client using the anon key."""
    global _api_client
    if _api_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set for API")
        _api_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _api_client


def verify_api_key(x_api_key: str | None = Header(default=None)):
    if settings.ENV == "production" and not settings.API_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Server misconfigured: API_SECRET_KEY required in production")
    if not settings.API_SECRET_KEY:
        return  # Dev mode: allow without key
    if x_api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def get_db() -> DBManager:
    """Return the DBManager singleton (uses service role key - for admin only)."""
    return DBManager()


class APIDBManager:
    """Lightweight wrapper for API read operations using anon key."""

    def __init__(self, client: Client):
        self.client = client


def get_api_db() -> APIDBManager:
    """Return a read-only DB wrapper for API endpoints (uses anon key)."""
    return APIDBManager(get_api_client())
