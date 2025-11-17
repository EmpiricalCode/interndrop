"""
Base scraper class with common scraping logic.
"""
import json
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from pathlib import Path
from src.utils.config import Config


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.

    Subclasses must implement the fetch() method to define
    how pages are fetched (headed vs headless browser).
    """

    def __init__(self):
        """Initialize the scraper."""
        self.client = Config.get_openai_client()

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
        Clean HTML and extract text content.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        return cleaned_text

    def parse(self, cleaned_text: str) -> list[dict]:
        """
        Parse cleaned HTML text using OpenAI to extract job listings.

        Args:
            cleaned_text: Cleaned text content from the page

        Returns:
            List of job dictionaries
        """
        # Get path to system prompt in src/shared/
        project_root = Path(__file__).parent.parent.parent
        prompt_path = project_root / "shared" / "system_prompt.txt"

        # Read the system prompt from the file
        with open(prompt_path, 'r') as f:
            system_prompt = f.read()

        # Create a chat completion using the OpenAI API
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": "CAREERS PAGE:\n" + cleaned_text
                }
            ],
            model=Config.OPENAI_MODEL,
        )

        return json.loads(chat_completion.choices[0].message.content)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity ratio between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity ratio between 0.0 and 1.0
        """
        return SequenceMatcher(None, text1, text2).ratio()

    def scrape_all_pages(self, base_url: str, max_pages: int = None, page = "page") -> list[dict]:
        """
        Scrape all pages with pagination until no more jobs or duplicate pages found.

        Args:
            base_url: Career page URL with optional pagination parameter
            max_pages: Maximum pages to scrape (defaults to Config.MAX_PAGES_PER_COMPANY)

        Returns:
            List of job dictionaries
        """
        if max_pages is None:
            max_pages = Config.MAX_PAGES_PER_COMPANY

        all_jobs = []
        seen_job_titles = set()
        i = 1

        while i <= max_pages:
            try:
                # Construct the URL for the current page
                if i == 1:
                    paginated_url = base_url
                else:
                    paginated_url = f"{base_url}&{page}={i}"
                print(f"Scraping page {i}: {paginated_url}")

                # Fetch the cleaned text content of the page
                cleaned_text = self.fetch(paginated_url)

                # If the fetched text is empty or indicates no results, stop.
                if not cleaned_text:
                    print("No more content found. Stopping.")
                    break


                # Parse the text to get a list of job objects
                jobs_on_page = self.parse(cleaned_text)

                # If parsing returns an empty list, it means no more jobs were found
                if not jobs_on_page:
                    print(f"Page {i} returned no jobs. Stopping.")
                    break
                
                # Check for similarity with the last page's content to detect duplicate pages
                if i > 1 and self.calculate_similarity(cleaned_text, last_cleaned_text) > 0.98:
                    print(f"Page {i} is too similar to the previous page. Stopping.")
                    break
                last_cleaned_text = cleaned_text

                # Normalize and collect job titles from the current page
                current_page_titles = {
                    job['title'].lower().replace(' ', '')
                    for job in jobs_on_page if 'title' in job
                }

                # If all jobs on the current page have been seen before, stop
                if current_page_titles.issubset(seen_job_titles):
                    print(f"Page {i} contains only duplicate jobs. Stopping.")
                    break

                # Add the found jobs to the aggregate list and update seen titles
                all_jobs.extend(jobs_on_page)
                seen_job_titles.update(current_page_titles)

                print(jobs_on_page)

                print(f"Found {len(jobs_on_page)} jobs on page {i}.")

                i += 1

            except Exception as e:
                # If any error occurs (e.g., network error, page not found), stop.
                print(f"An error occurred on page {i}: {e}. Stopping.")
                break

        return all_jobs
