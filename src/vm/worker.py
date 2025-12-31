"""
VM Scraping Worker Module
"""

import queue
import sys
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor

# Add project root to Python path FIRST
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Now import from src
from src.core.fetch.base import BaseFetcher
from src.core.fetch import HeadedFetcher
from src.core.scraper.posting import PostingScraper
from src.core.scraper.listing import ListingScraper
from src.core.repository import CompanyRepository
from src.models.company import Company
from src.models import Listing
from src.utils.config import Config

listing_queue = queue.Queue()

def scrape_all_companies(listing_queue: queue.Queue):
    """
    Scrapes all companies listed in the shared companies.json file,
    adding scraped listings to the provided listing queue.
    Uses multi-threading to scrape multiple companies concurrently.

    TODO: Save into RDS
    """
    company_repo = CompanyRepository()
    companies = company_repo.get_all()

    print(f"Loaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    print(f"\nStarting company scraper pool with {Config.THREAD_POOL_SIZE} threads...\n")

    # Shared fetcher instance for all threads
    shared_fetcher = HeadedFetcher()
    num_listings = 0
    num_listings_lock = threading.Lock()

    def scrape_company(company):
        """Helper function to scrape a single company."""
        nonlocal num_listings
        try:
            print(f"[Thread {threading.current_thread().name}] Scraping {company.name}...")

            listing_scraper = ListingScraper(fetcher=shared_fetcher)
            listings = listing_scraper.scrape_all_pages(company)

            # Update listing count
            with num_listings_lock:
                num_listings += len(listings)

            # Enqueue listings for parsing
            for listing in listings:
                listing_queue.put((company, listing))

            print(f"[Thread {threading.current_thread().name}] Found {len(listings)} listings from {company.name}")

        except Exception as e:
            print(f"[Thread {threading.current_thread().name}] Error scraping {company.name}: {e}")

    # Use thread pool to scrape companies concurrently
    with ThreadPoolExecutor(max_workers=Config.THREAD_POOL_SIZE) as executor:
        executor.map(scrape_company, companies)

    listing_queue.put(None)  # Signal completion

    print(f"\n\nTotal listings scraped: {num_listings}")

def parse_all_listings(listing_queue: queue.Queue):
    """
    Parse all listings from the listing queue.
    Single-threaded approach for processing postings sequentially.
    """
    print(f"\nStarting single-threaded parse worker...\n")

    # Create a fetcher instance
    fetcher = HeadedFetcher()

    while True:
        item = listing_queue.get()

        # Check for completion signal
        if item is None:
            print("\nListing queue finished.")
            break

        company, listing = item

        # Parse the listing
        parse_listing(company, listing, fetcher)

    print("All parsing tasks completed.")

def parse_listing(company: Company, listing: Listing, fetcher: BaseFetcher):
    """
    Parse a single listing and write the posting output to a text file for debugging.
    Each posting is saved in a separate file named by its hash ID.

    Args:
        company: Company object associated with the listing
        listing: Listing object to parse
        fetcher: Fetcher instance for fetching
    """
    try:
        # Use the fetcher instance
        posting_scraper = PostingScraper(fetcher=fetcher)

        print(f"Parsing: {listing.title} at {company.name}")

        # Scrape the posting
        posting = posting_scraper.scrape(listing, company)

        # TEMPORARY: Create output directory and save to file for debugging
        output_dir = project_root / "output" / "postings"
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{posting.id}.txt" if posting.id else f"{listing.hash()}.txt"
        output_path = output_dir / filename

        # Write posting data to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"POSTING DETAILS\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(f"ID: {posting.id}\n")
            f.write(f"Title: {posting.title}\n")
            f.write(f"Company: {posting.company}\n")
            f.write(f"Location: {posting.location}\n")
            f.write(f"Work Arrangement: {posting.work_arrangement}\n")
            f.write(f"Salary: ${posting.salary} ({posting.salary_type})\n")
            f.write(f"Term: {posting.term}\n")
            f.write(f"Categories: {', '.join(posting.categories) if posting.categories else 'None'}\n")
            f.write(f"URL: {posting.url}\n")
            f.write(f"\n{'=' * 80}\n")

        print(f"✓ Saved: {filename}")

    except Exception as e:
        print(f"✗ Error parsing {listing.title}: {e}")

if __name__ == "__main__":

    scrape_worker_thread = threading.Thread(target=scrape_all_companies, args=(listing_queue,))
    parse_worker_pool_thread = threading.Thread(target=parse_all_listings, args=(listing_queue,))

    # Start workers
    scrape_worker_thread.start()
    parse_worker_pool_thread.start()

    scrape_worker_thread.join()
    parse_worker_pool_thread.join()