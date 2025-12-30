"""
Core fetching and scraping logic - framework agnostic.
"""
from src.core.fetch import BaseFetcher, HeadedFetcher, HeadlessFetcher

__all__ = [
    'BaseFetcher',
    'HeadedFetcher',
    'HeadlessFetcher',
]