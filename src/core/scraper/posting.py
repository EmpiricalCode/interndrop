"""
Posting parser for processing job postings.
"""
from src.models.job import Job


class PostingScraper:
    """
    Parses job posting data and converts them to Job objects.
    Handles posting-specific processing and validation.
    """
