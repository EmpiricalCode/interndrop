import json
from pathlib import Path
from src.models import Company


class CompanyRepository:
    """Repository for loading companies from JSON configuration file."""

    def __init__(self):
        config_path = Path(__file__).parent.parent.parent / "shared" / "companies.json"
        with open(config_path) as f:
            data = json.load(f)
            self.companies = [Company(**company_dict) for company_dict in data["companies"]]

    def get_all(self) -> list[Company]:
        """Get all companies."""
        return self.companies

    def get_by_name(self, name: str) -> Company | None:
        """Get a company by name (case-insensitive)."""
        return next(
            (c for c in self.companies if c.name.lower() == name.lower()),
            None
        )
