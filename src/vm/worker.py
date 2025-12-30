"""
VM Scraping Worker Module
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.fetch import HeadedFetcher
from src.core.scraper.job import JobScraper
from src.core.repository import CompanyRepository
from src.models import Job

def scrape_all_companies():
    """
    Scrapes all companies listed in the shared companies.json file.

    TODO: Save into RDS
    """
    company_repo = CompanyRepository()
    companies = company_repo.get_all()[:3]

    print(f"Loaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    fetcher = HeadedFetcher()
    job_scraper = JobScraper(fetcher=fetcher)
    all_jobs = []

    for company in companies:
        print(f"\nScraping {company.name}...")
        try:
            # Scrape all pages for this company
            job_dicts = job_scraper.scrape_all_pages(company)

            # Convert job dicts to Job dataclass objects
            jobs = [Job(**job_dict) for job_dict in job_dicts]
            all_jobs.extend(jobs)

            print(f"Found {len(jobs)} jobs from {company.name}")
            for job in jobs:
                print(f"  - {job}")

        except Exception as e:
            print(f"Error scraping {company.name}: {e}")
            continue

    print(f"\n\nTotal jobs scraped: {len(all_jobs)}")


if __name__ == "__main__":
    scrape_all_companies()