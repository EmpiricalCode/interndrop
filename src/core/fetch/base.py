"""
Base fetcher class with common fetching logic.
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseFetcher(ABC):
    """
    Abstract base class for web fetchers.

    Subclasses must implement the fetch() method to define
    how pages are fetched (headed vs headless browser).
    """

    @abstractmethod
    def fetch(self, url: str) -> str:
        """
        Fetch and clean HTML content from a URL.

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
