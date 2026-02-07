import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.RAW_DATA_DIR = self.DATA_DIR / "raw"
        self.CURRENT_DATA_DIR = self.DATA_DIR / "current"
        self.ARCHIVE_DIR = self.DATA_DIR / "archive"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        self.MANUAL_DATA_DIR = self.BASE_DIR / "manually_scrapped_data"

        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

        self.DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

        self.SCRAPE_DELAY_SECONDS = int(os.getenv("SCRAPE_DELAY_SECONDS", "3"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

        self.ENV = os.getenv("ENV", "development")

        self.API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")
        self.API_HOST = os.getenv("API_HOST", "127.0.0.1")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_ALLOWED_ORIGINS = [
            o.strip()
            for o in os.getenv("API_ALLOWED_ORIGINS", "*").split(",")
            if o.strip()
        ]

        self.EWU_BASE_URL = "https://www.ewubd.edu"
        self.EWU_ADMISSION_URL = "https://admission.ewubd.edu"

    def validate(self, require_supabase=True):
        """Validate that required settings are configured.

        Returns a list of missing/invalid settings.
        """
        issues = []

        if require_supabase:
            if not self.SUPABASE_URL:
                issues.append("SUPABASE_URL is not set")
            if not self.SUPABASE_SERVICE_ROLE_KEY:
                issues.append("SUPABASE_SERVICE_ROLE_KEY is not set")

        return issues

    def ensure_directories(self):
        """Create required directories if they don't exist."""
        for d in [self.DATA_DIR, self.RAW_DATA_DIR, self.CURRENT_DATA_DIR,
                   self.ARCHIVE_DIR, self.LOGS_DIR]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
