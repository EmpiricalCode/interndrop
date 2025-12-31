"""
Performance comparison test for single-threaded vs multi-threaded company scraping.
"""

import sys
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.fetch import HeadedFetcher
from src.core.scraper.listing import ListingScraper
from src.core.repository import CompanyRepository
from src.utils.config import Config


def single_threaded_approach(companies):
    """
    Single-threaded approach: scrape all companies sequentially.

    Args:
        companies: List of Company objects to scrape

    Returns:
        tuple: (elapsed_time, total_listings)
    """
    start_time = time.time()

    fetcher = HeadedFetcher()
    total_listings = 0

    for company in companies:
        try:
            print(f"[Single-threaded] Scraping {company.name}...")
            listing_scraper = ListingScraper(fetcher=fetcher)
            listings = listing_scraper.scrape_all_pages(company)
            total_listings += len(listings)
            print(f"[Single-threaded] Found {len(listings)} listings from {company.name}")
        except Exception as e:
            print(f"[Single-threaded] Error scraping {company.name}: {e}")

    elapsed_time = time.time() - start_time
    return elapsed_time, total_listings


def multi_threaded_approach(companies):
    """
    Multi-threaded approach: scrape companies concurrently using thread pool.

    Args:
        companies: List of Company objects to scrape

    Returns:
        tuple: (elapsed_time, total_listings)
    """
    start_time = time.time()

    # Shared fetcher instance for all threads (enforces global rate limiting)
    shared_fetcher = HeadedFetcher()
    total_listings = 0
    listings_lock = threading.Lock()

    def scrape_company(company):
        """Helper function to scrape a single company."""
        nonlocal total_listings
        try:
            print(f"[Multi-threaded - Thread {threading.current_thread().name}] Scraping {company.name}...")
            listing_scraper = ListingScraper(fetcher=shared_fetcher)
            listings = listing_scraper.scrape_all_pages(company)

            with listings_lock:
                total_listings += len(listings)

            print(f"[Multi-threaded - Thread {threading.current_thread().name}] Found {len(listings)} listings from {company.name}")
        except Exception as e:
            print(f"[Multi-threaded - Thread {threading.current_thread().name}] Error scraping {company.name}: {e}")

    # Use thread pool to scrape companies concurrently
    with ThreadPoolExecutor(max_workers=Config.THREAD_POOL_SIZE) as executor:
        executor.map(scrape_company, companies)

    elapsed_time = time.time() - start_time
    return elapsed_time, total_listings


def run_performance_test():
    """
    Run the performance comparison test.

    This test:
    1. Loads all companies from the repository
    2. Runs multi-threaded scraping and times it
    3. Runs single-threaded scraping and times it
    4. Compares the results
    """
    print("=" * 80)
    print("COMPANY SCRAPING PERFORMANCE COMPARISON TEST")
    print("=" * 80)

    # Load companies
    company_repo = CompanyRepository()
    companies = company_repo.get_all()[:5]

    if not companies:
        print("No companies found in repository!")
        return

    print(f"\nLoaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    print(f"\nThread pool size: {Config.THREAD_POOL_SIZE}")
    print(f"Min crawl delay: {Config.MIN_CRAWL_DELAY}s")

    # Run multi-threaded test first
    print("\n" + "=" * 80)
    print("MULTI-THREADED APPROACH")
    print("=" * 80)
    multi_time, multi_listings = multi_threaded_approach(companies)
    print(f"\n✓ Multi-threaded completed in {multi_time:.2f}s")
    print(f"  Total listings scraped: {multi_listings}")

    # Wait a bit between tests
    print("\nWaiting 5 seconds before single-threaded test...")
    time.sleep(5)

    # Run single-threaded test
    print("\n" + "=" * 80)
    print("SINGLE-THREADED APPROACH")
    print("=" * 80)
    single_time, single_listings = single_threaded_approach(companies)
    print(f"\n✓ Single-threaded completed in {single_time:.2f}s")
    print(f"  Total listings scraped: {single_listings}")

    # Compare results
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print(f"Single-threaded time: {single_time:.2f}s ({single_time/60:.2f} minutes)")
    print(f"Multi-threaded time:  {multi_time:.2f}s ({multi_time/60:.2f} minutes)")

    if multi_time < single_time:
        speedup = single_time / multi_time
        time_saved = single_time - multi_time
        print(f"\n🚀 Multi-threaded is {speedup:.2f}x faster!")
        print(f"   Time saved: {time_saved:.2f}s ({time_saved/60:.2f} minutes)")
    else:
        slowdown = multi_time / single_time
        print(f"\n⚠️  Multi-threaded is {slowdown:.2f}x slower")
        print(f"   (This might happen with rate limiting or small datasets)")

    # Verify both approaches got the same number of listings
    if multi_listings == single_listings:
        print(f"\n✓ Both approaches scraped the same number of listings: {multi_listings}")
    else:
        print(f"\n⚠️  Different listing counts! Multi: {multi_listings}, Single: {single_listings}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    run_performance_test()
