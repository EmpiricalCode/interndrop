"""
Test script to scrape Coinbase careers page using headed (visible) browser.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from src.core import HeadedScraper

def test_coinbase_headed_scrape():
    """Test scraping Coinbase internship positions with headed browser."""
    url = "https://www.coinbase.com/en-ca/careers/positions?department=Internships%2520%2526%2520Emerging%2520Talent%2520Positions"

    print("="*60)
    print("HEADED BROWSER TEST - Coinbase Internships")
    print("="*60)
    print("\nInitializing HeadedScraper (visible browser)...")
    scraper = HeadedScraper()

    print(f"Scraping: {url}\n")
    jobs = scraper.scrape_all_pages(url)

    print(f"\n{'='*60}")
    print(f"RESULTS: {len(jobs)} jobs found")
    print(f"{'='*60}\n")

    print(json.dumps(jobs, indent=2))

    return jobs

if __name__ == "__main__":
    test_coinbase_headed_scrape()
