import re
import time

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class AcademicCalendarScraper(BaseScraper):
    """Scrape academic calendar from EWU website.

    Only scrapes the latest year tab. Data is fully replaced each run.
    """

    name = "academic_calendar"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/academic-calendar"]

    def _get_latest_year_links(self, soup) -> list[tuple[str, str]]:
        """Extract detail page links from the latest (first) year tab.

        Returns list of (link_text, full_url) tuples.
        """
        # Year tabs use anchor links like <a href="#2026">2026</a>
        # Find the first (latest) year by looking at tab links
        tab_links = soup.find_all("a", href=re.compile(r"^#\d{4}$"))
        if not tab_links:
            logger.warning(f"[{self.name}] No year tabs found")
            return []

        # First tab link is the latest year
        latest_year = tab_links[0].get_text(strip=True)
        logger.info(f"[{self.name}] Latest year tab: {latest_year}")

        # Find all detail links on the page that belong to the latest year.
        # Detail links look like: /academic-calendar-details/spring-2026
        # We collect ALL detail links, then filter to those containing the year.
        all_detail_links = soup.find_all(
            "a", href=re.compile(r"/academic-calendar-details/")
        )

        results = []
        for link in all_detail_links:
            href = link.get("href", "")
            text = link.get_text(strip=True)
            # Only include links that reference the latest year
            if latest_year in text or latest_year in href:
                full_url = href
                if not full_url.startswith("http"):
                    full_url = f"{settings.EWU_BASE_URL}{href}"
                results.append((text, full_url))

        logger.info(f"[{self.name}] Found {len(results)} detail links for {latest_year}")
        return results

    def _determine_calendar_type(self, slug: str, link_text: str) -> str:
        """Determine if this is an exam schedule or academic calendar."""
        combined = f"{slug} {link_text}".lower()
        if "exam" in combined or "schedule-final" in combined:
            return "exam_schedule"
        return "academic_calendar"

    def _extract_program_and_semester(self, soup, link_text: str) -> tuple[str, str]:
        """Extract program_type and semester from the detail page.

        Falls back to the link text if page elements aren't found.
        """
        program_type = ""
        semester = ""

        # Try to find program type from h4 heading like
        # "Academic Calendar for Undergraduate Programs (Except B.Pharm and LL.B)"
        for h4 in soup.find_all("h4"):
            text = h4.get_text(strip=True)
            if "academic calendar" in text.lower() and "program" in text.lower():
                # Strip "Academic Calendar for " prefix
                program_type = re.sub(
                    r"(?i)^academic\s+calendar\s+for\s+", "", text
                ).strip()
                break

        # Try to find semester from h3 heading like "Spring 2026"
        for h3 in soup.find_all("h3"):
            text = h3.get_text(strip=True)
            if re.match(r"(Spring|Summer|Fall)\s+\d{4}", text, re.IGNORECASE):
                semester = text.strip()
                break

        # Fallbacks from link text
        if not semester:
            m = re.search(r"(Spring|Summer|Fall)\s+\d{4}", link_text, re.IGNORECASE)
            if m:
                semester = m.group(0)

        if not program_type:
            program_type = link_text

        return program_type, semester

    def _parse_detail_page(
        self, html: str, url: str, link_text: str
    ) -> list[dict]:
        """Parse a single academic calendar detail page."""
        soup = self.get_soup(html)
        slug = url.rstrip("/").split("/")[-1]
        calendar_type = self._determine_calendar_type(slug, link_text)
        program_type, semester = self._extract_program_and_semester(soup, link_text)

        if not semester:
            logger.warning(f"[{self.name}] Could not determine semester for {url}")
            return []

        records = []
        table = soup.find("table")
        if not table:
            logger.warning(f"[{self.name}] No table found on {url}")
            return []

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            event_date = cells[0].get_text(strip=True)
            day = cells[1].get_text(strip=True)
            event_name = cells[2].get_text(strip=True)

            # Skip header row (Date / Day / Event)
            if event_date.lower() == "date" and day.lower() == "day":
                continue

            # Skip empty rows
            if not event_date or not event_name:
                continue

            records.append({
                "semester": semester,
                "program_type": program_type,
                "calendar_type": calendar_type,
                "event_date": event_date,
                "day": day or None,
                "event_name": event_name,
                "source_url": url,
            })

        logger.info(
            f"[{self.name}] Parsed {len(records)} events from {url} "
            f"({semester} / {program_type} / {calendar_type})"
        )
        return records

    def parse(self, html: str, url: str) -> list[dict]:
        """Parse the main calendar page: extract latest year links, then fetch each."""
        soup = self.get_soup(html)
        links = self._get_latest_year_links(soup)

        if not links:
            logger.warning(f"[{self.name}] No detail links found")
            return []

        all_records = []
        for i, (link_text, detail_url) in enumerate(links):
            logger.info(f"[{self.name}] Fetching detail page: {detail_url}")
            detail_html = self.fetch(detail_url)
            if detail_html is None:
                continue

            records = self._parse_detail_page(detail_html, detail_url, link_text)
            all_records.extend(records)

            # Respectful delay between detail page requests
            if i < len(links) - 1:
                time.sleep(self.delay)

        return all_records
