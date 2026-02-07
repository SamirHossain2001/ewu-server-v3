"""Shared fixtures for EWU Database API integration tests.

All tests hit the real Supabase database — no mocks, no fakes.
"""

import json

import pytest
from fastapi.testclient import TestClient

from api.main import app
from config.settings import settings
from database.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def _check_db_connection():
    """Skip entire test suite if Supabase is unreachable or anon key missing."""
    if not settings.SUPABASE_ANON_KEY:
        pytest.skip("SUPABASE_ANON_KEY not set")
    db = DBManager()
    if not db.test_connection():
        pytest.skip("Supabase connection unavailable")


@pytest.fixture
def client():
    """Real FastAPI TestClient — no mocks, hits real Supabase."""
    headers = {}
    if settings.API_SECRET_KEY:
        headers["X-Api-Key"] = settings.API_SECRET_KEY
    with TestClient(app, headers=headers) as c:
        yield c


@pytest.fixture
def db():
    """Real DBManager for fetching valid IDs/slugs in test setup."""
    return DBManager()


@pytest.fixture
def data_dir():
    return settings.MANUAL_DATA_DIR


@pytest.fixture
def sample_programs():
    filepath = settings.MANUAL_DATA_DIR / "all_available_programs.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("programs", [])
    return []


@pytest.fixture
def sample_clubs():
    filepath = settings.MANUAL_DATA_DIR / "clubs.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("clubs", [])
    return []


@pytest.fixture
def sample_tuition():
    filepath = settings.MANUAL_DATA_DIR / "tution_fees.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
