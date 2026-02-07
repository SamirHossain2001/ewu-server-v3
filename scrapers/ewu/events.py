import re
from datetime import datetime

from scrapers.base_scraper import BaseScraper
from config.settings import settings


class EventsScraper(BaseScraper):
    name = "events"

    @staticmethod
    def _parse_date(date_str: str) -> tuple[str | None, str | None]:
        """Parse date range like '15 Nov, 2025 To 15 Nov, 2025' into ISO dates."""
        if not date_str:
            return None, None
        parts = re.split(r'\s+To\s+', date_str, flags=re.IGNORECASE)
        dates = []
        for part in parts:
            part = part.strip()
            for fmt in ("%d %b, %Y", "%d %B, %Y", "%d %b %Y", "%Y-%m-%d"):
                try:
                    dates.append(datetime.strptime(part, fmt).strftime("%Y-%m-%d"))
                    break
                except ValueError:
                    continue
            else:
                dates.append(None)
        start = dates[0] if dates else None
        end = dates[1] if len(dates) > 1 else None
        return start, end

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/events"]

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)
        events = []

        # Each event is inside a .event-details container
        event_containers = soup.select(".event-details")

        for container in event_containers:
            # Title from h3 inside .event-head
            title = ""
            h3 = container.select_one(".event-head h3")
            if h3:
                title = h3.get_text(strip=True)

            if not title or len(title) < 5:
                continue

            # Date and location from <span> siblings of the h3
            event_date = ""
            location = ""
            head_div = container.select_one(".event-head .margin-bottom10")
            if head_div:
                spans = head_div.find_all("span")
                if len(spans) >= 1:
                    event_date = spans[0].get_text(strip=True)
                if len(spans) >= 2:
                    location = spans[1].get_text(strip=True)

            # URL from Read More link
            event_url = ""
            link = container.select_one("a[href*='/single-event/']")
            if link:
                event_url = link.get("href", "")
                if event_url and not event_url.startswith("http"):
                    event_url = f"{settings.EWU_BASE_URL}{event_url}"

            start_date, end_date = self._parse_date(event_date)

            events.append({
                "title": title,
                "description": "",
                "event_date": start_date,
                "end_date": end_date,
                "location": location,
                "url": event_url,
                "source_url": url,
            })

        return events
