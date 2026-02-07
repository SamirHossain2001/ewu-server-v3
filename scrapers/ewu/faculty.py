from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class FacultyScraper(BaseScraper):
    """The faculty search page uses AJAX/Select2 dropdowns to filter by department.
    This scraper attempts to call the underlying API directly. If that fails,
    it falls back to static page parsing.
    """

    name = "faculty"

    DEPARTMENTS = [
        "cse", "eee", "ice", "ce", "pharmacy", "geb", "mps",
        "dsa",  # Data Science and Analytics
        "bba", "economics",
        "english", "law", "sociology", "information-studies", "pphs",
        "ier",  # Institute of Education and Research
    ]

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/search-faculty"]

    def run(self) -> list[dict]:
        """Override run to handle AJAX-based faculty search."""
        logger.info(f"[{self.name}] Starting faculty scrape...")
        all_faculty = []

        api_data = self._try_api_approach()
        if api_data:
            all_faculty = api_data
        else:
            # Fallback: parse the static search page
            logger.info(f"[{self.name}] API approach failed, trying static page parse")
            html = self.fetch(self.get_urls()[0])
            if html:
                all_faculty = self.parse(html, self.get_urls()[0])

        if self.validate(all_faculty):
            self.save(all_faculty)

        logger.info(f"[{self.name}] Scrape complete: {len(all_faculty)} faculty members")
        return all_faculty

    def _try_api_approach(self) -> list[dict]:
        """Try to fetch faculty data from the search API endpoint."""
        faculty = []

        api_urls = [
            f"{settings.EWU_BASE_URL}/api/faculty",
            f"{settings.EWU_BASE_URL}/search-faculty/search",
            f"{settings.EWU_BASE_URL}/faculty/search",
        ]

        for api_url in api_urls:
            try:
                resp = self.session.get(
                    api_url,
                    headers={"X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        faculty = data
                    elif isinstance(data, dict) and "data" in data:
                        faculty = data["data"]

                    if faculty:
                        logger.info(f"[{self.name}] Found {len(faculty)} faculty via API: {api_url}")
                        return [self._normalize(f, api_url) for f in faculty]
            except Exception:
                continue

        return []

    def _normalize(self, record: dict, url: str) -> dict:
        """Normalize a faculty record from API or page parse to match DB schema."""
        profile_url = record.get("profile_url", record.get("profile_link", ""))
        if profile_url and not profile_url.startswith("http"):
            profile_url = f"{settings.EWU_BASE_URL}{profile_url}"

        # Extract profile_id from profile URL: /faculty-profile/john-doe -> john-doe
        profile_id = ""
        if profile_url:
            profile_id = profile_url.rstrip("/").split("/")[-1]

        return {
            "name": record.get("name", ""),
            "designation": record.get("designation", record.get("position", "")),
            "department_name": record.get("department_name", record.get("department", "")),
            "email": record.get("email", ""),
            "phone": record.get("phone", ""),
            "profile_url": profile_url,
            "profile_id": profile_id,
            "image_url": record.get("image_url", record.get("image", "")),
            "specialization": record.get("specialization", ""),
            "academic_background": None,
            "publications": None,
            "details": None,
            "source_url": url,
        }

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        faculty = []

        cards = soup.select(
            ".faculty-card, .faculty-item, .member-item, "
            ".card, .team-member, .profile-card"
        )

        for card in cards:
            name_el = card.find(["h3", "h4", "h5", "a"])
            name = name_el.get_text(strip=True) if name_el else ""

            if not name:
                continue

            designation_el = card.find(["p", "span"], class_=lambda c: c and "designation" in str(c).lower())
            designation = designation_el.get_text(strip=True) if designation_el else ""

            dept_el = card.find(["p", "span"], class_=lambda c: c and "dept" in str(c).lower())
            department_name = dept_el.get_text(strip=True) if dept_el else ""

            email_el = card.find("a", href=lambda h: h and "mailto:" in str(h))
            email = email_el.get("href", "").replace("mailto:", "") if email_el else ""

            profile_url = ""
            link_el = card.find("a", href=lambda h: h and "faculty-profile" in str(h))
            if link_el:
                profile_url = link_el.get("href", "")
                if profile_url and not profile_url.startswith("http"):
                    profile_url = f"{settings.EWU_BASE_URL}{profile_url}"

            profile_id = ""
            if profile_url:
                profile_id = profile_url.rstrip("/").split("/")[-1]

            faculty.append({
                "name": name,
                "designation": designation,
                "department_name": department_name,
                "email": email,
                "phone": "",
                "profile_url": profile_url,
                "profile_id": profile_id,
                "image_url": "",
                "specialization": "",
                "academic_background": None,
                "publications": None,
                "details": None,
                "source_url": url,
            })

        return faculty
