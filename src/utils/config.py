"""
Configuration management for InternDrop.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

class Config:
    """Central configuration class."""

    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    # Scraping Configuration
    MAX_PAGES_PER_COMPANY = int(os.getenv('MAX_PAGES_PER_COMPANY', 20))
    PAGE_SIMILARITY_THRESHOLD = float(os.getenv('PAGE_SIMILARITY_THRESHOLD', 0.8))
    FETCH_TIMEOUT_MS = int(os.getenv('FETCH_TIMEOUT_MS', 20000))
    MIN_CRAWL_DELAY = int(os.getenv('MIN_CRAWL_DELAY', 10))

    # VM Configuration
    THREAD_POOL_SIZE = int(os.getenv('THREAD_POOL_SIZE', 5))

    # OpenAI client singleton
    _openai_client = None

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """
        Get or create OpenAI client (lazy singleton).
        Reuses the same client instance across the application.

        Returns:
            OpenAI client instance

        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        if cls._openai_client is None:
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            cls._openai_client = OpenAI(api_key=cls.OPENAI_API_KEY)
        return cls._openai_client

    @classmethod
    def validate(cls):
        """Validate required configuration is present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")