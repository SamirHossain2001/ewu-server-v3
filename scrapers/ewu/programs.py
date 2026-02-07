from scrapers.base_scraper import BaseScraper
from config.settings import settings


class ProgramsScraper(BaseScraper):
    name = "programs"

    def get_urls(self) -> list[str]:
        return [
            f"{settings.EWU_BASE_URL}/undergraduate-programs",
            f"{settings.EWU_BASE_URL}/graduate-programs",
        ]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        programs = []

        level = "Undergraduate" if "undergraduate" in url else "Graduate"

        # EWU program pages typically list programs in card/list sections grouped by department
        # Look for common patterns: headings for departments, list items for programs
        sections = soup.select(".faculty-section, .program-list, .content-area section")

        if not sections:
            # Fallback: try to parse from general content structure
            sections = [soup.find("main") or soup.find("div", class_="content") or soup.body]

        for section in sections:
            if section is None:
                continue

            # Try to find department/faculty headings
            current_faculty = ""
            current_department = ""

            for element in section.find_all(["h2", "h3", "h4", "li", "a", "p", "div"]):
                tag = element.name
                text = element.get_text(strip=True)

                if not text:
                    continue

                if tag in ("h2", "h3") and "faculty" in text.lower():
                    current_faculty = text
                elif tag in ("h3", "h4") and "department" in text.lower():
                    current_department = text
                elif tag in ("li", "a") and any(
                    kw in text.lower()
                    for kw in ["bachelor", "master", "b.sc", "m.sc", "bba", "mba", "llb", "b.pharm"]
                ):
                    programs.append({
                        "name": text,
                        "degree_type": level,
                        "faculty": current_faculty,
                        "department": current_department,
                        "source_url": url,
                    })

        return programs
