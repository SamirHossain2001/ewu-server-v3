from scrapers.base_scraper import BaseScraper
from config.settings import settings


class AboutScraper(BaseScraper):
    name = "about"

    def get_urls(self) -> list[str]:
        return [
            f"{settings.EWU_BASE_URL}/history",
            f"{settings.EWU_BASE_URL}/vision-mission-ewu",
        ]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)

        content = soup.find("main") or soup.find("div", class_="content") or soup.body
        if not content:
            return []

        if "history" in url:
            section = "history"
        elif "vision" in url:
            section = "vision_mission"
        else:
            section = "about"

        data = {
            "section": section,
            "title": "",
            "content": [],
            "source_url": url,
        }

        title_el = content.find(["h1", "h2"])
        if title_el:
            data["title"] = title_el.get_text(strip=True)

        for element in content.find_all(["h2", "h3", "h4", "p", "li"]):
            text = element.get_text(strip=True)
            if text:
                data["content"].append({
                    "type": element.name,
                    "text": text,
                })

        return [data]
