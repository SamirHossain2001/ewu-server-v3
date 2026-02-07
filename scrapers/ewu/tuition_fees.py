import re

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger

# Map raw HTML table headers to DB column names
HEADER_MAP = {
    "name of programs": "program",
    "name of faculties": "_faculty",
    "tuition fee per credit": "fee_per_credit",
    "tuition fees": "total_tuition",
    "library, lab & activities fees": "library_lab_fees",
    "admission fee": "admission_fee",
    "grand total": "grand_total",
    "credits": "credits",
}


def _parse_money(value: str):
    """Parse '6,500/=' or '200,000/=' into a numeric value."""
    if not value:
        return None
    cleaned = re.sub(r'[^0-9.]', '', value.replace(',', ''))
    try:
        return float(cleaned) if '.' in cleaned else int(cleaned)
    except (ValueError, TypeError):
        return None


class TuitionFeesScraper(BaseScraper):
    name = "tuition_fees"

    def get_urls(self) -> list[str]:
        return [
            f"{settings.EWU_BASE_URL}/undergraduate-tuition-fees",
            f"{settings.EWU_BASE_URL}/graduate-programs-tuition-fees",
        ]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        fees = []

        level = "Undergraduate" if "undergraduate" in url else "Graduate"

        tables = soup.find_all("table")

        for table in tables:
            headers = []
            for th in table.find_all("th"):
                raw = th.get_text(strip=True).lower()
                headers.append(HEADER_MAP.get(raw, raw))

            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if not cells:
                    continue

                record = {"level": level, "source_url": url}

                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    if i < len(headers):
                        record[headers[i]] = text

                # Skip rows without a program name (e.g. serial number rows)
                program = record.get("program", "")
                if not program or program.lower().startswith("sl"):
                    continue

                for field in ("fee_per_credit", "total_tuition", "library_lab_fees",
                              "admission_fee", "grand_total"):
                    if field in record:
                        record[field] = _parse_money(record[field])

                if "credits" in record:
                    try:
                        record["credits"] = int(float(record["credits"]))
                    except (ValueError, TypeError):
                        record["credits"] = None

                record.pop("_faculty", None)

                fees.append(record)

        if not fees:
            logger.warning(f"[{self.name}] No fee records found from {url}")

        return fees
