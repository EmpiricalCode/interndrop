"""
Test script to verify hash consistency across multiple scrapes.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
from src.core.fetch import HeadedFetcher
from src.core.scraper.listing import ListingScraper
from src.core.repository import CompanyRepository
from src.models.listing import Listing
from src.models.company import Company

def test_hash_consistency(company: Company):
    """
    Test that scraping the same careers page twice produces identical hashes.

    Args:
        company: Company object to scrape
    """
    print("="*60)
    print("HASH CONSISTENCY TEST")
    print("="*60)
    print("\nInitializing HeadedFetcher for first scrape...\n")
    fetcher = HeadedFetcher()
    listing_scraper = ListingScraper(fetcher=fetcher)

    print(f"First scrape: {company.url}\n")
    listings_first = listing_scraper.scrape_all_pages(company)

    print(f"\n{'='*60}")
    print(f"FIRST SCRAPE: {len(listings_first)} listings found")
    print(f"{'='*60}\n")

    # Convert first scrape to Listing objects and create hash-to-listing mapping
    first_listings = [Listing(**listing) for listing in listings_first]
    first_hash_to_listing = {listing.hash(): listing for listing in first_listings}
    first_hashes = set(first_hash_to_listing.keys())

    print(f"Waiting before second scrape...\n")
    print(f"Second scrape: {company.url}\n")
    listings_second = listing_scraper.scrape_all_pages(company)

    print(f"\n{'='*60}")
    print(f"SECOND SCRAPE: {len(listings_second)} listings found")
    print(f"{'='*60}\n")

    # Convert second scrape to Listing objects and create hash-to-listing mapping
    second_listings = [Listing(**listing) for listing in listings_second]
    second_hash_to_listing = {listing.hash(): listing for listing in second_listings}
    second_hashes = set(second_hash_to_listing.keys())

    # Compare hashes
    print(f"\n{'='*60}")
    print("HASH COMPARISON")
    print(f"{'='*60}\n")

    print(f"First scrape hashes: {len(first_hashes)}")
    print(f"Second scrape hashes: {len(second_hashes)}")

    if first_hashes == second_hashes:
        print("\n✓ SUCCESS: All hashes match between scrapes!")
        print(f"  Total unique listings: {len(first_hashes)}")
    else:
        print("\n✗ FAILURE: Hashes do not match!")
        only_in_first = first_hashes - second_hashes
        only_in_second = second_hashes - first_hashes

        if only_in_first:
            print(f"\n  Listings only in FIRST scrape ({len(only_in_first)}):")
            for hash_val in only_in_first:
                listing = first_hash_to_listing[hash_val]
                print(f"    - {listing.title}")
                print(f"      Location: {', '.join(listing.location)}")
                print(f"      Department: {listing.department}")
                print(f"      Hash: {hash_val}")
                print()

        if only_in_second:
            print(f"\n  Listings only in SECOND scrape ({len(only_in_second)}):")
            for hash_val in only_in_second:
                listing = second_hash_to_listing[hash_val]
                print(f"    - {listing.title}")
                print(f"      Location: {', '.join(listing.location)}")
                print(f"      Department: {listing.department}")
                print(f"      Hash: {hash_val}")
                print()

    print(f"\n{'='*60}\n")

    return first_hashes == second_hashes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test hash consistency by scraping a careers page twice"
    )
    parser.add_argument(
        "company_name",
        nargs="?",
        default="Stripe",
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

    test_hash_consistency(company)
