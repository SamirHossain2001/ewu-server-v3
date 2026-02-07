from datetime import datetime, timezone

from supabase import create_client, Client

from config.settings import settings
from utils.logger import logger


class DBManager:
    """Singleton database manager for Supabase operations."""

    _instance = None
    _client: Client | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> Client:
        if self._client is None:
            issues = settings.validate(require_supabase=True)
            if issues:
                raise RuntimeError(f"Database configuration errors: {', '.join(issues)}")
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        return self._client

    def get_all(self, table: str) -> list[dict]:
        """Fetch all records from a table."""
        try:
            response = self.client.table(table).select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch from {table}: {e}")
            return []

    def upsert(self, table: str, data: list[dict], on_conflict: str = "id",
               batch_size: int = 500) -> bool:
        """Upsert records into a table in batches.

        Args:
            table: Target table name.
            data: List of record dicts.
            on_conflict: Column(s) to use for conflict resolution.
            batch_size: Max records per API call.
        """
        if not data:
            return True

        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self.client.table(table).upsert(batch, on_conflict=on_conflict).execute()
                logger.info(f"Upserted batch {i // batch_size + 1} ({len(batch)} records) into {table}")
            logger.info(f"Upserted {len(data)} total records into {table}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert into {table}: {e}")
            return False

    def insert(self, table: str, data: list[dict]) -> bool:
        """Insert records into a table."""
        if not data:
            return True

        try:
            self.client.table(table).insert(data).execute()
            logger.info(f"Inserted {len(data)} records into {table}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert into {table}: {e}")
            return False

    def delete_all(self, table: str) -> bool:
        """Delete all records from a table."""
        try:
            # Supabase requires a filter for delete; use a truthy condition
            self.client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            logger.info(f"Deleted all records from {table}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete from {table}: {e}")
            return False

    def log_scrape(self, scraper_name: str, records: int, status: str,
                   error_message: str = "", duration: float = 0.0):
        """Log a scrape run to the metadata table."""
        try:
            self.client.table("scrape_metadata").insert({
                "scraper_name": scraper_name,
                "last_run": datetime.now(timezone.utc).isoformat(),
                "records_scraped": records,
                "status": status,
                "error_message": error_message,
                "duration_seconds": duration,
            }).execute()
        except Exception as e:
            logger.error(f"Failed to log scrape metadata: {e}")

    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            self.client.table("scrape_metadata").select("id").limit(1).execute()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
