import re

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class GovernanceScraper(BaseScraper):
    name = "governance"

    BODIES = {
        "board_of_trustees": f"{settings.EWU_BASE_URL}/board-trustees",
        "syndicate": f"{settings.EWU_BASE_URL}/syndicate",
        "academic_council": f"{settings.EWU_BASE_URL}/academic-council",
    }

    def get_urls(self) -> list[str]:
        return list(self.BODIES.values())

    def run(self) -> list[dict]:
        """Override run to scrape each governance body separately."""
        logger.info(f"[{self.name}] Starting scrape...")
        all_members = []

        for body, url in self.BODIES.items():
            html = self.fetch(url)
            if html is None:
                logger.warning(f"[{self.name}] Could not fetch {body} from {url}")
                continue

            members = self._parse_body(html, url, body)
            all_members.extend(members)
            logger.info(f"[{self.name}] {body}: {len(members)} members")

        if self.validate(all_members):
            self.save(all_members)

        logger.info(f"[{self.name}] Scrape complete: {len(all_members)} total members")
        return all_members

    def _parse_body(self, html: str, url: str, body: str) -> list[dict]:
        soup = self.get_soup(html)
        members = []
        seen_names = set()

        # Members are shown as linked cards with h4 (name) and h6 (role)
        # Look for links to /office-employee/ pages
        member_links = soup.find_all("a", href=re.compile(r"/office-employee/"))

        for link in member_links:
            name_el = link.find("h4")
            name = name_el.get_text(strip=True) if name_el else link.get_text(strip=True)

            if not name or len(name) < 3 or name in seen_names:
                continue
            seen_names.add(name)

            role_el = link.find("h6")
            role = role_el.get_text(strip=True) if role_el else ""

            profile_url = link.get("href", "")
            if profile_url and not profile_url.startswith("http"):
                profile_url = f"{settings.EWU_BASE_URL}{profile_url}"

            is_chairperson = "chairperson" in role.lower() or "chairman" in role.lower()

            members.append({
                "body": body,
                "name": name,
                "role": role,
                "is_chairperson": is_chairperson,
                "profile_url": profile_url,
                "source_url": url,
            })

        # Fallback: if no /office-employee/ links found, try h4 + h6 pairs
        if not members:
            headings = soup.find_all("h4")
            for h4 in headings:
                name = h4.get_text(strip=True)
                if not name or len(name) < 3 or name in seen_names:
                    continue

                # Skip navigation/UI headings
                if any(skip in name.lower() for skip in ["menu", "footer", "search", "contact"]):
                    continue

                seen_names.add(name)
                h6 = h4.find_next_sibling("h6")
                role = h6.get_text(strip=True) if h6 else ""
                is_chairperson = "chairperson" in role.lower() or "chairman" in role.lower()

                members.append({
                    "body": body,
                    "name": name,
                    "role": role,
                    "is_chairperson": is_chairperson,
                    "profile_url": "",
                    "source_url": url,
                })

        return members

    def parse(self, html: str, url: str) -> list[dict]:
        # Required by BaseScraper but we use _parse_body instead
        return self._parse_body(html, url, "unknown")
