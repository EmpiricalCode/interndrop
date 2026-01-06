"""
VM Scraping Worker Module
"""

import queue
import sys
import time
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
from src.core.repository import CompanyRepository, PostingRepository
from src.models.company import Company
from src.models import Listing
from src.utils.config import Config

listing_queue = queue.Queue()

def scrape_all_companies(listing_queue: queue.Queue, fetcher: BaseFetcher):
    """
    Scrapes all companies listed in the shared companies.json file,
    adding scraped listings to the provided listing queue.
    Uses multi-threading to scrape multiple companies concurrently.

    Args:
        listing_queue: Queue to add scraped listings to
        fetcher: Shared fetcher instance for all threads

    TODO: Save into RDS
    """
    company_repo = CompanyRepository()
    companies = company_repo.get_all()

    print(f"Loaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    print(f"\nStarting company scraper pool with {Config.THREAD_POOL_SIZE} threads...\n")
    num_listings = 0
    num_listings_lock = threading.Lock()

    def scrape_company(company):
        """Helper function to scrape a single company."""
        nonlocal num_listings
        try:
            print(f"[Thread {threading.current_thread().name}] Scraping {company.name}...")

            listing_scraper = ListingScraper(fetcher=fetcher)
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

def parse_all_listings(listing_queue: queue.Queue, fetcher: BaseFetcher):
    """
    Parse all listings from the listing queue.
    Single-threaded approach for processing postings sequentially.

    Args:
        listing_queue: Queue containing listings to parse
        fetcher: Shared fetcher instance
    """
    print(f"\nStarting single-threaded parse worker...\n")

    # Create repository
    posting_repo = PostingRepository()

    # Fetch all existing posting IDs from database
    print("Fetching all existing posting IDs from database...")
    existing_postings = posting_repo.get_all()
    existing_posting_ids = {posting.id for posting in existing_postings}
    del existing_postings  # Free memory - we only need the IDs
    print(f"Found {len(existing_posting_ids)} existing postings in database\n")

    # Track all listing IDs that were processed
    processed_listing_ids = set()

    while True:
        item = listing_queue.get()

        # Check for completion signal
        if item is None:
            print("\nListing queue finished.")
            break

        company, listing = item

        # Generate the posting ID (same way the scraper does it)
        posting_id = listing.hash()

        # Check if posting ID already exists in database
        if posting_id in existing_posting_ids:
            print(f"${company.name}: ✓ Posting already exists: {posting_id}")
        else:
            # Parse the listing and create new posting
            parse_listing(company, listing, fetcher, posting_repo)
        
        processed_listing_ids.add(posting_id)

    # Delete postings that were not in the processed list
    posting_ids_to_delete = [posting_id for posting_id in existing_posting_ids if posting_id not in processed_listing_ids]
    if posting_ids_to_delete:
        print(f"\nDeleting {len(posting_ids_to_delete)} postings that are no longer in listings...")
        deleted_count = posting_repo.bulk_delete(posting_ids_to_delete)
        print(f"${company.name}: ✓ Deleted {deleted_count} postings from database")

    print("All parsing tasks completed.")

def parse_listing(company: Company, listing: Listing, fetcher: BaseFetcher, posting_repo: PostingRepository):
    """
    Parse a single listing and create a new posting in the database.

    Args:
        company: Company object associated with the listing
        listing: Listing object to parse
        fetcher: Fetcher instance for fetching
        posting_repo: PostingRepository instance for database operations
    """
    try:
        # Use the fetcher instance
        posting_scraper = PostingScraper(fetcher=fetcher)

        print(f"Parsing: {listing.title} at {company.name}")

        # Scrape the posting
        posting = posting_scraper.scrape(listing, company)

        # Create the posting in the database
        posting_repo.create(posting)
        print(f"${company.name}: ✓ Created new posting: {posting.id}")

    except Exception as e:
        print(f"${company.name}: ✗ Error parsing {listing.title}: {e}")

if __name__ == "__main__":
    # Create single shared fetcher instance
    shared_fetcher = HeadedFetcher()

    scrape_worker_thread = threading.Thread(target=scrape_all_companies, args=(listing_queue, shared_fetcher))
    parse_worker_pool_thread = threading.Thread(target=parse_all_listings, args=(listing_queue, shared_fetcher))

    # Start workers
    scrape_worker_thread.start()
    parse_worker_pool_thread.start()

    scrape_worker_thread.join()
    parse_worker_pool_thread.join()