"""
Job parser for extracting job information from parsed data.
"""
import json
from pathlib import Path
from difflib import SequenceMatcher
from src.models.listing import Listing
from src.models.company import Company
from src.utils.config import Config


class ListingScraper:
    """
    Parses job data dictionaries and converts them to Listing objects.
    Also handles parsing cleaned HTML text using OpenAI to extract job listings.
    """

    def __init__(self, fetcher=None):
        """Initialize the listing scraper.

        Args:
            fetcher: Optional fetcher instance to use for scraping all pages.
                     Required if using scrape_all_pages method.
        """
        self.client = Config.get_openai_client()
        self.fetcher = fetcher

    def parse(self, cleaned_text: str, company_name: str) -> list[Listing]:
        """
        Parse cleaned HTML text using OpenAI to extract job listings.

        Args:
            cleaned_text: Cleaned text content from the page
            company_name: Name of the company for the listings

        Returns:
            List of Listing objects
        """
        # Get path to system prompt in src/shared/
        project_root = Path(__file__).parent.parent.parent
        prompt_path = project_root / "shared" / "listing_scraper_prompt.txt"

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
            temperature=0
        )

        # Parse JSON response and convert to Listing objects
        job_dicts = json.loads(chat_completion.choices[0].message.content)
        listings = []
        for job_dict in job_dicts:
            listing = Listing(
                title=job_dict.get("title", ""),
                location=job_dict.get("location", []),
                term=job_dict.get("term", []),
                department=job_dict.get("department", ""),
                work_arrangement=job_dict.get("work_arrangement", ""),
                href=job_dict.get("href", ""),
                href_is_url=job_dict.get("href_is_url", True),
                company=company_name,
            )
            listings.append(listing)

        return listings

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

    def scrape_all_pages(self, company: Company, max_pages: int = None) -> list[Listing]:
        """
        Scrape all pages with pagination until no more jobs or duplicate pages found.

        Args:
            company: Company object containing URL and pagination settings
            max_pages: Maximum pages to scrape (defaults to Config.MAX_PAGES_PER_COMPANY)

        Returns:
            List of Listing objects
        """
        if self.fetcher is None:
            raise ValueError("Fetcher instance is required to scrape all pages")

        if max_pages is None:
            max_pages = Config.MAX_PAGES_PER_COMPANY
        if not company.paged:
            max_pages = 1

        all_jobs = []
        seen_job_titles = set()
        i = 1

        while i <= max_pages:
            try:
                # Construct the URL for the current page
                if not company.paged or not company.page_query_param:
                    formatted_url = company.url
                else:
                    formatted_url = f"{company.url}&{company.page_query_param}={i}"
                print(f"{company.name}: Scraping page {i}: {formatted_url}\n")

                # Fetch the cleaned text content of the page
                cleaned_text = self.fetcher.fetch(formatted_url)

                # If the fetched text is empty or indicates no results, stop.
                if not cleaned_text:
                    print(f"{company.name}: No more content found. Stopping.")
                    break

                # Parse the text to get a list of Listing objects
                jobs_on_page = self.parse(cleaned_text, company.name)

                # If parsing returns an empty list, it means no more jobs were found
                if not jobs_on_page:
                    print(f"{company.name}: Page {i} returned no jobs. Stopping.")
                    break

                # Check for similarity with the last page's content to detect duplicate pages
                if i > 1 and self.calculate_similarity(cleaned_text, last_cleaned_text) > 0.98:
                    print(f"{company.name}: Page {i} is too similar to the previous page. Stopping.")
                    break
                last_cleaned_text = cleaned_text

                # Normalize and collect job titles from the current page
                current_page_titles = {
                    job.title.lower().replace(' ', '')
                    for job in jobs_on_page
                }

                # If all jobs on the current page have been seen before, stop
                if current_page_titles.issubset(seen_job_titles):
                    print(f"{company.name}: Page {i} contains only duplicate jobs. Stopping.")
                    break

                # Add the found jobs to the aggregate list and update seen titles
                all_jobs.extend(jobs_on_page)
                seen_job_titles.update(current_page_titles)

                print(f"{company.name}: Found {len(jobs_on_page)} jobs on page {i}.\n")

                i += 1

            except Exception as e:
                # If any error occurs (e.g., network error, page not found), stop.
                print(f"{company.name}: An error occurred on page {i}: {e}. Stopping.")
                break

        return all_jobs

