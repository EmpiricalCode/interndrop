"""
Base fetcher class with common fetching logic.
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import time
from src.utils.config import Config


class BaseFetcher(ABC):
    """
    Abstract base class for web fetchers.

    Subclasses must implement the _fetch_impl() method to define
    how pages are fetched (headed vs headless browser).
    """

    def __init__(self):
        """Initialize the fetcher with rate limiting tracking."""
        self._last_fetch_time = 0

    def fetch(self, url: str) -> str:
        """
        Fetch and clean HTML content from a URL with rate limiting.

        This method enforces a minimum delay between fetches using
        Config.MIN_CRAWL_DELAY to be respectful to servers.

        Args:
            url: The URL to fetch

        Returns:
            Cleaned text content from the page
        """
        # Calculate time since last fetch
        time_since_last_fetch = time.time() - self._last_fetch_time

        # If not enough time has passed, wait
        if time_since_last_fetch < Config.MIN_CRAWL_DELAY:
            print("Fetch delay...\n")
            wait_time = Config.MIN_CRAWL_DELAY - time_since_last_fetch
            time.sleep(wait_time)

        # Perform the actual fetch
        result = self._fetch_impl(url)

        # Update last fetch time
        self._last_fetch_time = time.time()

        return result

    @abstractmethod
    def _fetch_impl(self, url: str) -> str:
        """
        Implementation-specific fetch logic.

        Subclasses must implement this method to define
        how pages are fetched (headed vs headless browser).

        Args:
            url: The URL to fetch

        Returns:
            Cleaned text content from the page
        """
        pass

    def clean_html(self, html: str) -> str:
        """
        Clean HTML and extract text content, including links with their hrefs.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content with links formatted as "text (href)"
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        # This is so the LLM can extract links
        # Replace <a> tags with "text (href)" format
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href:
                link_text = link.get_text(strip=True)
                link.replace_with(f"{link_text} (HREF: {href})")

        # Get text and clean it up
        text = soup.get_text()

        # Normalize Unicode punctuation to ASCII equivalents
        text = text.replace('\u2013', '-')  # en dash
        text = text.replace('\u2014', '-')  # em dash
        text = text.replace('\u2018', "'")  # left single quote
        text = text.replace('\u2019', "'")  # right single quote
        text = text.replace('\u201c', '"')  # left double quote
        text = text.replace('\u201d', '"')  # right double quote
        text = text.replace('\u2026', '...')  # ellipsis

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        return cleaned_text
