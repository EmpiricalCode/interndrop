"""
Scraper module with base and specialized scraper implementations.
"""
from src.core.scraper.base import BaseScraper
from src.core.scraper.headed import HeadedScraper
from src.core.scraper.headless import HeadlessScraper

__all__ = [
    'BaseScraper',
    'HeadedScraper',
    'HeadlessScraper',
]
