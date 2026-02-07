from scrapers.base_scraper import BaseScraper
from config.settings import settings


class ClubsScraper(BaseScraper):
    name = "clubs"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/clubs"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        clubs = []

        # Each club is inside a div.ewu-clubs-member-details container
        club_elements = soup.select(".ewu-clubs-member-details")

        for elem in club_elements:
            name_el = elem.find("h4")
            name = name_el.get_text(strip=True) if name_el else ""

            if not name or len(name) < 3:
                continue

            # Club URL from the "Visit Now" button
            link = ""
            link_el = elem.select_one("a.btn-ewu-clubs-now")
            if link_el:
                link = link_el.get("href", "")
                if link and not link.startswith("http"):
                    link = f"{settings.EWU_BASE_URL}{link}"

            # Club logo from .ewu-clubs-img img
            logo = ""
            img_el = elem.select_one(".ewu-clubs-img img")
            if img_el:
                logo = img_el.get("src", "")
                if logo and not logo.startswith("http"):
                    logo = f"{settings.EWU_BASE_URL}{logo}"

            clubs.append({
                "name": name,
                "description": "",
                "url": link,
                "logo": logo,
                "source_url": url,
            })

        return clubs
