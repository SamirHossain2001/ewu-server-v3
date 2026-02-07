import re

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class AdmissionDeadlinesScraper(BaseScraper):
    name = "admission_deadlines"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_ADMISSION_URL}/index.php?documentid=importantdates.php"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        deadlines = []

        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue

            # Try to determine the level (Undergraduate/Graduate) from context
            level = "Undergraduate"
            prev = table.find_previous(["h2", "h3", "h4", "h5", "strong", "b"])
            if prev:
                prev_text = prev.get_text(strip=True).lower()
                if "graduate" in prev_text and "undergraduate" not in prev_text:
                    level = "Graduate"

            # Detect semester from page content
            semester = ""
            page_text = soup.get_text()
            sem_match = re.search(r"(Spring|Summer|Fall|Winter)\s+(\d{4})", page_text, re.IGNORECASE)
            if sem_match:
                semester = f"{sem_match.group(1)} {sem_match.group(2)}"

            # Parse header row
            headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]

            for row in rows[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 2:
                    continue

                # Try to map cells to fields based on headers
                record = {
                    "program": "",
                    "department": "",
                    "level": level,
                    "semester": semester,
                    "application_deadline": "",
                    "admission_test_date": "",
                    "source_url": url,
                }

                for i, cell in enumerate(cells):
                    if i >= len(headers):
                        break
                    h = headers[i]
                    if "program" in h or "department" in h:
                        record["program"] = cell
                    elif "deadline" in h or "last date" in h or "application" in h:
                        record["application_deadline"] = cell
                    elif "test" in h or "exam" in h or "admission test" in h:
                        record["admission_test_date"] = cell

                if record["program"]:
                    deadlines.append(record)

        return deadlines
