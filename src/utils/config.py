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
    PAGE_SIMILARITY_THRESHOLD = float(os.getenv('PAGE_SIMILARITY_THRESHOLD', 0.98))
    FETCH_TIMEOUT_MS = int(os.getenv('FETCH_TIMEOUT_MS', 10000))

    # OpenAI client singleton
    _openai_client = None

    @classmethod
    def get_openai_client(self) -> OpenAI:
        """
        Get or create OpenAI client (lazy singleton).
        Reuses the same client instance across the application.

        Returns:
            OpenAI client instance

        Raises:
            ValueError: If OPENAI_API_KEY is not set
        """
        if self._openai_client is None:
            if not self.validate():
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self._openai_client = OpenAI(api_key=self.OPENAI_API_KEY)
        return self._openai_client

    @classmethod
    def validate(self):
        """Validate required configuration is present."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")