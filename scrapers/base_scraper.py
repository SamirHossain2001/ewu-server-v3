import json
import time
import random
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from config.settings import settings
from utils.logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


class BaseScraper(ABC):
    name: str = "base"

    def __init__(self):
        self.session = requests.Session()
        self.delay = settings.SCRAPE_DELAY_SECONDS
        self.max_retries = settings.MAX_RETRIES
        self.timeout = settings.REQUEST_TIMEOUT

    def fetch(self, url: str) -> str | None:
        """Fetch a URL with retry logic and exponential backoff.

        Returns the response text, or None on failure.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                resp = self.session.get(url, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                logger.debug(f"[{self.name}] Fetched {url} (status {resp.status_code})")
                return resp.text
            except requests.RequestException as e:
                wait = 2 ** attempt
                logger.warning(
                    f"[{self.name}] Attempt {attempt}/{self.max_retries} failed for {url}: {e}. "
                    f"Retrying in {wait}s..."
                )
                if attempt < self.max_retries:
                    time.sleep(wait)

        logger.error(f"[{self.name}] All {self.max_retries} attempts failed for {url}")
        return None

    @staticmethod
    def get_soup(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    def get_urls(self) -> list[str]:
        """Return the list of URLs this scraper needs to fetch."""

    @abstractmethod
    def parse(self, html: str, url: str) -> list[dict]:
        """Parse HTML content and return structured data records."""

    def validate(self, data: list[dict]) -> bool:
        """Basic validation: data must be a non-empty list of dicts."""
        if not data:
            logger.warning(f"[{self.name}] Validation failed: empty data")
            return False
        if not all(isinstance(r, dict) for r in data):
            logger.warning(f"[{self.name}] Validation failed: not all records are dicts")
            return False
        return True

    def save(self, data: list[dict]):
        """Save scraped data to JSON file with metadata."""
        settings.ensure_directories()
        output_path = settings.CURRENT_DATA_DIR / f"{self.name}.json"

        output = {
            "metadata": {
                "scraper": self.name,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "record_count": len(data),
                "source_urls": self.get_urls(),
            },
            "data": data,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"[{self.name}] Saved {len(data)} records to {output_path}")

    def run(self) -> list[dict]:
        """Execute the full scrape pipeline: fetch -> parse -> validate -> save."""
        logger.info(f"[{self.name}] Starting scrape...")
        all_data = []

        urls = self.get_urls()
        for i, url in enumerate(urls):
            html = self.fetch(url)
            if html is None:
                continue

            records = self.parse(html, url)
            all_data.extend(records)

            # Respectful delay between requests
            if i < len(urls) - 1:
                time.sleep(self.delay)

        if not self.validate(all_data):
            logger.error(f"[{self.name}] Scrape failed validation")
            return []

        self.save(all_data)
        logger.info(f"[{self.name}] Scrape complete: {len(all_data)} records")
        return all_data
