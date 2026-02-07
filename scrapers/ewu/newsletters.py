import re

from scrapers.base_scraper import BaseScraper
from config.settings import settings


class NewslettersScraper(BaseScraper):
    name = "newsletters"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/newsletters"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        newsletters = []

        # Each newsletter is in a .news-letter-col container
        items = soup.select(".news-letter-col")

        if not items:
            # Fallback: look for .news-letter-wrap
            items = soup.select(".news-letter-wrap")

        for item in items:
            # Title from .program-name
            title_el = item.select_one(".program-name")
            title = title_el.get_text(strip=True) if title_el else ""

            if not title:
                continue

            # Image from .news-letter-photo img
            image_url = ""
            img_el = item.select_one(".news-letter-photo img")
            if img_el:
                image_url = img_el.get("src", "")
                if image_url and not image_url.startswith("http"):
                    image_url = f"{settings.EWU_BASE_URL}{image_url}"

            # PDF URL from download link (a.btn-program)
            pdf_url = ""
            pdf_el = item.select_one("a.btn-program")
            if pdf_el:
                pdf_url = pdf_el.get("href", "")
                if pdf_url and not pdf_url.startswith("http"):
                    pdf_url = f"{settings.EWU_BASE_URL}{pdf_url}"

            # Date from .news-letter-date-wrap
            published_date = ""
            date_el = item.select_one(".news-letter-date-wrap")
            if date_el:
                published_date = date_el.get_text(strip=True)

            # Extract semester and year from title (e.g. "Newsletter Fall 2025")
            semester = ""
            year = ""
            match = re.search(r"(Spring|Summer|Fall|Winter)\s+(\d{4})", title, re.IGNORECASE)
            if match:
                semester = match.group(1)
                year = match.group(2)

            newsletters.append({
                "title": title,
                "published_date": published_date,
                "semester": semester,
                "year": year,
                "image_url": image_url,
                "pdf_url": pdf_url,
                "source_url": url,
            })

        return newsletters
