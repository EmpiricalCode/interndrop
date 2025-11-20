"""
VM Scraping Worker Module
"""

from src.core.scraper import HeadedScraper
from src.core.repository import CompanyRepository
from src.models import Company, Job


def scrape_all_companies():
    """
    Scrapes all companies listed in the shared companies.json file.

    TODO: Save into RDS
    """
    company_repo = CompanyRepository()
    companies = company_repo.get_all()

    print(f"Loaded {len(companies)} companies:")
    for company in companies:
        print(f"  - {company.name}")

    scraper = HeadedScraper()
    all_jobs = []

    for company in companies:
        print(f"\nScraping {company.name}...")
        try:
            # Determine pagination parameters
            page_param = company.page_query_param if company.paged else ""

            # Scrape all pages for this company
            job_dicts = scraper.scrape_all_pages(
                base_url=company.url,
                page=page_param
            )

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