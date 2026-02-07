from scrapers.base_scraper import BaseScraper
from config.settings import settings


class ScholarshipsScraper(BaseScraper):
    name = "scholarships"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/scholarships-financial-aid"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        scholarships = []

        content = soup.find("main") or soup.find("div", class_="content") or soup.body
        if not content:
            return scholarships

        current_scholarship = None

        for element in content.find_all(["h2", "h3", "h4", "p", "li", "table"]):
            tag = element.name
            text = element.get_text(strip=True)

            if not text:
                continue

            if tag in ("h2", "h3", "h4"):
                if current_scholarship and current_scholarship.get("name"):
                    scholarships.append(current_scholarship)

                current_scholarship = {
                    "name": text,
                    "description": "",
                    "eligibility": [],
                    "source_url": url,
                }
            elif current_scholarship:
                if tag == "p":
                    if current_scholarship["description"]:
                        current_scholarship["description"] += " " + text
                    else:
                        current_scholarship["description"] = text
                elif tag == "li":
                    current_scholarship["eligibility"].append(text)
                elif tag == "table":
                    current_scholarship["table_data"] = self._parse_table(element)

        # Don't forget the last one
        if current_scholarship and current_scholarship.get("name"):
            scholarships.append(current_scholarship)

        return [self._transform(s) for s in scholarships]

    @staticmethod
    def _transform(record: dict) -> dict:
        """Map scraped fields to DB schema columns."""
        eligibility = record.get("eligibility", [])
        if isinstance(eligibility, list):
            eligibility = "; ".join(eligibility) if eligibility else ""

        return {
            "name": record.get("name", ""),
            "description": record.get("description", ""),
            "eligibility": eligibility,
            "source_url": record.get("source_url", ""),
        }

    @staticmethod
    def _parse_table(table) -> list[dict]:
        """Extract table data as list of row dicts."""
        rows = []
        headers = [th.get_text(strip=True) for th in table.find_all("th")]

        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if not cells:
                continue
            if headers:
                row = dict(zip(headers, cells))
            else:
                row = {f"col_{i}": c for i, c in enumerate(cells)}
            rows.append(row)

        return rows
