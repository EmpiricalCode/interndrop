"""
VM Scraping Worker Module
"""

import queue
import sys
from pathlib import Path
import threading

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.fetch import HeadedFetcher
from src.core.scraper.listing import ListingScraper
from src.core.repository import CompanyRepository
from src.models import Listing

listing_queue = queue.Queue()

def scrape_all_companies(listing_queue):
    """
    Scrapes all companies listed in the shared companies.json file,
    adding scraped listings to the provided listing queue.

    TODO: Save into RDS
    """
    company_repo = CompanyRepository()
    companies = company_repo.get_all()

    print(f"Loaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    fetcher = HeadedFetcher()
    listing_scraper = ListingScraper(fetcher=fetcher)
    num_listings = 0

    for company in companies:
        print(f"\nScraping {company.name}...")
        try:
            # Scrape all pages for this company
            listing_dicts = listing_scraper.scrape_all_pages(company)

            # Convert listing dicts to Listing dataclass objects
            listings = [Listing(**listing_dict) for listing_dict in listing_dicts]
            num_listings += len(listings)

            # Enqueue listings for parsing
            for listing in listings:
                listing_queue.put(listing)

            print(f"Found {len(listings)} listings from {company.name}")
            for listing in listings:
                print(f"  - {listing}")

        except Exception as e:
            print(f"Error scraping {company.name}: {e}")
            continue

    listing_queue.put(None)  # Signal completion

    print(f"\n\nTotal listings scraped: {num_listings}")

def parse_all_listings(listing_queue):
    """
    Parse all listings from the listing queue.
    """
    pass

if __name__ == "__main__":

    scrape_worker_thread = threading.Thread(target=scrape_all_companies, args=(listing_queue,))
    parse_worker_pool_thread = threading.Thread(target=parse_all_listings, args=(listing_queue,))

    # Start workers
    scrape_worker_thread.start()
    parse_worker_pool_thread.start()

    scrape_worker_thread.join()
    parse_worker_pool_thread.join()