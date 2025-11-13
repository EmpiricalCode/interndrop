"""
Core scraping logic - framework agnostic.
"""
from src.core.scraper import BaseScraper, HeadedScraper, HeadlessScraper

__all__ = [
    'BaseScraper',
    'HeadedScraper',
    'HeadlessScraper',
]