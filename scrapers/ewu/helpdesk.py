from scrapers.base_scraper import BaseScraper
from config.settings import settings


class HelpdeskScraper(BaseScraper):
    name = "helpdesk"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/notice-details/online-helpdesk-list-email-accounts"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        contacts = []

        # The helpdesk data is in plain HTML tables
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue

            header_row = rows[0]
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]

            if not headers:
                continue

            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue

                cell_texts = [c.get_text(strip=True) for c in cells]

                # Extract email from mailto: link if present
                email = ""
                email_el = row.find("a", href=lambda h: h and "mailto:" in str(h))
                if email_el:
                    email = email_el.get("href", "").replace("mailto:", "").strip()
                else:
                    # Look for email-like text in cells
                    for text in cell_texts:
                        if "@" in text:
                            email = text
                            break

                if not email:
                    continue

                department = ""
                full_name = ""
                purpose = ""

                for i, cell_text in enumerate(cell_texts):
                    if i >= len(headers):
                        break
                    h = headers[i]
                    if "group" in h or "department" in h or "name" in h:
                        department = cell_text
                    elif "purpose" in h or "description" in h:
                        purpose = cell_text

                category = "academic"
                admin_keywords = ["accounts", "registrar", "admission", "library",
                                  "hr", "ict", "it", "admin", "exam", "controller"]
                dept_lower = department.lower()
                if any(kw in dept_lower for kw in admin_keywords):
                    category = "administrative"

                contacts.append({
                    "category": category,
                    "department_code": department,
                    "full_name": department,  # Page doesn't have individual names
                    "email": email,
                    "purpose": purpose,
                    "source_url": url,
                })

        return contacts
