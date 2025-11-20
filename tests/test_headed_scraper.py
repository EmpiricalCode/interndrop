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
from src.core import HeadedScraper

def test_headed_scrape(url: str):
    """
    Test scraping a careers page with headed browser.

    Args:
        url: The careers page URL to scrape
    """
    print("="*60)
    print("HEADED BROWSER TEST")
    print("="*60)
    print("\nInitializing HeadedScraper (visible browser)...\n")
    scraper = HeadedScraper()

    print(f"Scraping: {url}\n")
    jobs = scraper.scrape_all_pages(url, page="current_page")

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(jobs)} jobs found")
    print(f"{'='*60}\n")

    print(json.dumps(jobs, indent=2))

    return jobs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test headed browser scraper on a careers page"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://www.citadel.com/careers/open-opportunities?experience-filter=internships&selected-job-sections=388,389,387,390&sort_order=DESC&per_page=10&action=careers_listing_filter",
        help="URL of the careers page to scrape (defaults to Coinbase internships)"
    )

    args = parser.parse_args()
    test_headed_scrape(args.url)
