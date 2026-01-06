"""
Test script to scrape careers pages using headed (visible) browser.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import argparse
from src.core.fetch import HeadedFetcher
from src.core.scraper.listing import ListingScraper
from src.core.repository import CompanyRepository
from src.models.company import Company

def test_headed_scrape(company: Company):
    """
    Test scraping a careers page with headed browser.

    Args:
        company: The company object to scrape
    """
    print("="*60)
    print("HEADED BROWSER TEST")
    print("="*60)
    print("\nInitializing HeadedFetcher (visible browser)...\n")
    fetcher = HeadedFetcher()
    listing_scraper = ListingScraper(fetcher=fetcher)

    print(f"Scraping: {company.url}\n")
    listings = listing_scraper.scrape_all_pages(company)

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(listings)} listings found")
    print(f"{'='*60}\n")

    # Print listings using their __str__ method
    for listing in listings:
        print(f"  - {listing}")

    return listings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test headed browser scraper on a careers page"
    )
    parser.add_argument(
        "company_name",
        nargs="?",
        default="Roblox",
        help="Name of the company to scrape (defaults to Stripe)"
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

    test_headed_scrape(company)
