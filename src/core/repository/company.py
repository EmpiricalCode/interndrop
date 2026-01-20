from supabase import create_client, Client
from src.models import Company
from src.utils.config import Config


class CompanyRepository:
    """Repository for managing companies in Supabase."""

    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = "Companies"

    def get_all(self) -> list[Company]:
        """Get all companies from Supabase."""
        response = self.client.table(self.table_name).select("*").execute()

        return [Company(**company_dict) for company_dict in response.data]

    def get_by_name(self, name: str) -> Company | None:
        """Get a company by name (case-insensitive) from Supabase."""
        response = self.client.table(self.table_name).select("*").ilike("name", name).execute()

        if response.data and len(response.data) > 0:
            return Company(**response.data[0])
        return None

    def get_by_id(self, company_id: str) -> Company | None:
        """Get a company by ID from Supabase."""
        response = self.client.table(self.table_name).select("*").eq("id", company_id).execute()

        if response.data and len(response.data) > 0:
            return Company(**response.data[0])
        return None

    def create(self, company: Company) -> Company:
        """Create a new company in Supabase."""
        company_dict = {
            "name": company.name,
            "url": company.url,
            "paged": company.paged,
            "page_query_param": company.page_query_param,
        }

        response = self.client.table(self.table_name).insert(company_dict).execute()

        if response.data and len(response.data) > 0:
            return Company(**response.data[0])
        return company
