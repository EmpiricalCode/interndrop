"""
Fetcher module with base and specialized fetcher implementations.
"""
from src.core.fetch.base import BaseFetcher
from src.core.fetch.headed import HeadedFetcher
from src.core.fetch.headless import HeadlessFetcher

__all__ = [
    'BaseFetcher',
    'HeadedFetcher',
    'HeadlessFetcher',
]
