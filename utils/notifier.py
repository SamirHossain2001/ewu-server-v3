import requests
from config.settings import settings
from utils.logger import logger


class Notifier:
    @staticmethod
    def send_discord(message: str, alert: bool = False):
        """Send a message to the configured Discord webhook.

        Args:
            message: The message content.
            alert: If True, prefix with alert indicator.
        """
        url = settings.DISCORD_WEBHOOK_URL
        if not url:
            logger.debug("Discord webhook URL not configured, skipping notification")
            return

        prefix = "🚨 **ALERT**" if alert else "✅ **Update**"
        payload = {"content": f"{prefix}\n{message}"}

        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            logger.info("Discord notification sent")
        except requests.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")

    @staticmethod
    def send_scrape_summary(scraper_name: str, records: int, changes: int, status: str):
        """Send a formatted scrape summary notification."""
        message = (
            f"**Scraper:** {scraper_name}\n"
            f"**Records:** {records}\n"
            f"**Changes:** {changes}\n"
            f"**Status:** {status}"
        )
        alert = status != "success"
        Notifier.send_discord(message, alert=alert)
