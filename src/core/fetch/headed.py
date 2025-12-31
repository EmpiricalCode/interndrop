"""
Headed (visible) browser fetcher for sites requiring full browser.
"""
from playwright.sync_api import sync_playwright
from src.core.fetch.base import BaseFetcher
from src.utils.config import Config


class HeadedFetcher(BaseFetcher):
    """
    Fetcher using a headed (visible) browser.
    """

    def __init__(self):
        """Initialize the headed fetcher."""
        super().__init__()

    def _fetch_impl(self, url: str) -> str:
        """
        Fetch HTML content using a visible browser.

        Args:
            url: The URL to fetch

        Returns:
            Cleaned text content from the page
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
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
