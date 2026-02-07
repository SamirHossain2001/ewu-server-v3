import time

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class NoticesScraper(BaseScraper):
    name = "notices"

    def get_urls(self) -> list[str]:
        # Notice board has pagination - start with page 1, discover total pages during parse
        return [f"{settings.EWU_BASE_URL}/notice-board"]

    def run(self) -> list[dict]:
        """Override run to handle pagination."""
        logger.info(f"[{self.name}] Starting scrape with pagination...")
        all_notices = []

        page = 1
        max_pages = 30  # Safety limit

        while page <= max_pages:
            url = f"{settings.EWU_BASE_URL}/notice-board?page={page}"
            html = self.fetch(url)
            if html is None:
                break

            notices = self.parse(html, url)
            if not notices:
                logger.info(f"[{self.name}] No notices on page {page}, stopping pagination")
                break

            all_notices.extend(notices)
            logger.info(f"[{self.name}] Page {page}: {len(notices)} notices (total: {len(all_notices)})")

            # Check if there's a next page
            soup = self.get_soup(html)
            if not self._has_next_page(soup, page):
                break

            page += 1
            time.sleep(self.delay)

        if self.validate(all_notices):
            self.save(all_notices)

        logger.info(f"[{self.name}] Scrape complete: {len(all_notices)} notices across {page} pages")
        return all_notices

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        notices = []

        # Notice pages typically have a list of notice items
        notice_elements = soup.select(
            ".notice-item, .notice-list li, .news-item, "
            "article, .card, .list-group-item"
        )

        if not notice_elements:
            # Fallback: look for links in the main content area
            content = soup.find("main") or soup.find("div", class_="content") or soup.body
            if content:
                notice_elements = content.find_all("a", href=True)

        for elem in notice_elements:
            title_el = elem.find(["h2", "h3", "h4", "h5", "a"])
            title = title_el.get_text(strip=True) if title_el else elem.get_text(strip=True)

            if not title or len(title) < 5:
                continue

            link = ""
            if title_el and title_el.name == "a":
                link = title_el.get("href", "")
            elif elem.name == "a":
                link = elem.get("href", "")

            if link and not link.startswith("http"):
                link = f"{settings.EWU_BASE_URL}{link}"

            # Try to find date
            date_el = elem.find(["time", "span", "small"], class_=lambda c: c and "date" in str(c).lower())
            date = date_el.get_text(strip=True) if date_el else ""

            notices.append({
                "title": title,
                "url": link,
                "published_date": date,
                "source_url": url,
            })

        return notices

    @staticmethod
    def _has_next_page(soup, current_page: int) -> bool:
        """Check if pagination has a next page."""
        pagination = soup.find("ul", class_="pagination") or soup.find("nav", class_="pagination")
        if not pagination:
            return False

        next_link = pagination.find("a", string=lambda s: s and ("next" in s.lower() or "›" in s or "»" in s))
        if next_link:
            return True

        # Check for page number link
        next_page_link = pagination.find("a", string=str(current_page + 1))
        return next_page_link is not None
