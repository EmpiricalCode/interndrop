"""
Headless browser scraper for standard websites.
"""
from playwright.sync_api import sync_playwright
from src.core.scraper.base import BaseScraper
from src.utils.config import Config


class HeadlessScraper(BaseScraper):
    """
    Scraper using a headless (invisible) browser.
    """

    def fetch(self, url: str) -> str:
        """
        Fetch HTML content using a headless browser.

        Args:
            url: The URL to fetch

        Returns:
            Cleaned text content from the page
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Try networkidle for timeout duration
            try:
                page.goto(url, wait_until="networkidle", timeout=Config.FETCH_TIMEOUT_MS)
                html = page.content()
            except:
                # If it times out, just continue with what's loaded
                print("Network idle timed out - continuing anyways")
                html = page.content()
            finally:
                browser.close()

            return self.clean_html(html)
