"""
Posting parser for processing job postings.
"""
import json
import time
from pathlib import Path
from src.models.company import Company
from src.models.posting import Posting
from src.models.listing import Listing
from src.utils.config import Config


class PostingScraper:
    """
    Parses job posting data and converts them to Posting objects.
    Handles posting-specific processing and validation using OpenAI.
    """

    def __init__(self, fetcher=None):
        """Initialize the posting scraper.

        Args:
            fetcher: Optional fetcher instance to use for scraping.
                     Required if using scrape method.
        """
        self.client = Config.get_openai_client()
        self.fetcher = fetcher

    def parse(self, cleaned_text: str, company_name: str, url: str = "") -> Posting:
        """
        Parse cleaned HTML text using OpenAI to extract posting information.

        Args:
            cleaned_text: Cleaned text content from the posting page
            company_name: Name of the company (fallback if not extracted from page)
            url: URL of the posting (optional)

        Returns:
            Posting object
        """
        # Get path to system prompt in src/shared/
        project_root = Path(__file__).parent.parent.parent
        prompt_path = project_root / "shared" / "posting_scraper_prompt.txt"

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
                    "content": "JOB POSTING:\n" + cleaned_text
                }
            ],
            model=Config.OPENAI_MODEL,
            temperature=0
        )

        # Parse JSON response and convert to Posting object
        posting_dict = json.loads(chat_completion.choices[0].message.content)

        # Handle salary which is now a nested dict with type and amount
        salary_info = posting_dict.get("salary", {"type": "none", "amount": 0})
        salary_amount = salary_info.get("amount", 0) if isinstance(salary_info, dict) else 0
        salary_type = salary_info.get("type", "none") if isinstance(salary_info, dict) else "none"

        # Handle location which should be a list in the prompt response
        location = posting_dict.get("location", [])

        # Handle term which should be a list in the prompt response
        term = posting_dict.get("term", [])
        term_str = ", ".join(term) if isinstance(term, list) else str(term)

        posting = Posting(
            title=posting_dict.get("title", ""),
            location=location,
            work_arrangement=posting_dict.get("work_arrangement", ""),
            salary=salary_amount,
            salary_type=salary_type,
            url=url,
            term=term_str,
            categories=posting_dict.get("categories", []),
            company=posting_dict.get("company", company_name) or company_name,
            fetched_at=int(time.time())
        )

        return posting

    def scrape(self, listing: Listing, company: Company) -> Posting:
        """
        Scrape a Listing's URL and return a detailed Posting object.
        If scraping fails or no URL is available, constructs a Posting from the Listing data.

        Args:
            listing: Listing object containing the job URL to scrape

        Returns:
            Posting object
        """
        if self.fetcher is None:
            raise ValueError("Fetcher instance is required to scrape")

        # Get the URL from the listing's href
        if listing.href_is_url:
            url = listing.href
        else:
            # Extract base URL from company.url (scheme + host)
            from urllib.parse import urlparse
            parsed = urlparse(company.url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            url = base_url + listing.href

        # If there's a URL, try to scrape it for detailed information
        if url:
            # Fetch the cleaned text content
            cleaned_text = self.fetcher.fetch(url)

            if cleaned_text:
                # Parse the text to get a detailed Posting object
                try:
                    posting = self.parse(cleaned_text, listing.company, url)
                    posting.id = listing.hash()
                    return posting
                except Exception as e:
                    print(f"Error parsing posting from {url}: {e}")
                    # Fall through to create Posting from Listing data

        # If no URL or scraping failed, construct Posting from Listing data
        return Posting(
            title=listing.title,
            location=", ".join(listing.location) if listing.location else "",
            work_arrangement=listing.work_arrangement,
            salary=0,  # No salary info available from listing
            salary_type="none",  # No salary info available from listing
            url=listing.href or "",
            term="",  # No term info available from listing
            categories=[],  # No categories available from listing
            company=listing.company,
            id=listing.hash(),
            fetched_at=int(time.time())
        )
