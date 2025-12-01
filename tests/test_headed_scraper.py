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
from src.core.repository import CompanyRepository
from src.models.company import Company

def test_headed_scrape(company: Company):
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

    print(f"Scraping: {company.url}\n")
    jobs = scraper.scrape_all_pages(company)

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
        "company_name",
        nargs="?",
        default="Citadel",
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
