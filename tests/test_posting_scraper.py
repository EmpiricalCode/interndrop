"""
Test script to scrape listings and then scrape detailed postings.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from src.core.fetch import HeadedFetcher
from src.core.scraper.listing import ListingScraper
from src.core.scraper.posting import PostingScraper
from src.core.repository import CompanyRepository
from src.models.company import Company

def test_posting_scrape(company: Company):
    """
    Test scraping listings and then detailed postings with headed browser.

    Args:
        company: The company object to scrape
    """
    print("="*60)
    print("POSTING SCRAPER TEST")
    print("="*60)
    print("\nInitializing HeadedFetcher (visible browser)...\n")
    fetcher = HeadedFetcher()
    listing_scraper = ListingScraper(fetcher=fetcher)
    posting_scraper = PostingScraper(fetcher=fetcher)

    # First, scrape all listings from the company careers page
    print(f"Scraping listings from: {company.url}\n")
    listings = listing_scraper.scrape_all_pages(company)

    print(f"\n{'='*60}")
    print(f"LISTINGS: {len(listings)} found")
    print(f"{'='*60}\n")

    # Print listings
    for listing in listings:
        print(f"  - {listing}")

    # Now scrape detailed postings for each listing
    print(f"\n{'='*60}")
    print(f"SCRAPING DETAILED POSTINGS")
    print(f"{'='*60}\n")

    postings = []
    for i, listing in enumerate(listings, 1):
        print(f"[{i}/{len(listings)}] Scraping: {listing.title}")
        try:
            posting = posting_scraper.scrape(listing, company)
            postings.append(posting)
            print(f"  ✓ Success: {posting.title}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print(f"\n{'='*60}")
    print(f"POSTINGS: {len(postings)} scraped")
    print(f"{'='*60}\n")

    # Print all postings
    for posting in postings:
        print(f"  - {posting}")

    return postings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test posting scraper on a careers page"
    )
    parser.add_argument(
        "company_name",
        nargs="?",
        default="Citadel",
        help="Name of the company to scrape (defaults to Ramp)"
    )

    args = parser.parse_args()

    # Load company from repository
    company_repo = CompanyRepository()
    company = company_repo.get_by_name(args.company_name)

    if not company:
        print(f"Error: Company '{args.company_name}' not found in companies.json")
        print("\nAvailable companies:")
        for c in company_repo.get_all():
            print(f"  - {c.name}")
        sys.exit(1)

    test_posting_scrape(company)
