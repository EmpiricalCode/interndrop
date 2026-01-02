from datetime import datetime
from supabase import create_client, Client
from src.models import Posting
from src.utils.config import Config


class PostingRepository:
    """Repository for managing postings in Supabase."""

    def __init__(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.table_name = "Postings"

    def _normalize_posting_data(self, data: dict) -> dict:
        """Normalize posting data from Supabase to match Posting model types."""
        normalized = data.copy()

        # Convert timestamp string to Unix timestamp (int)
        if "date" in normalized:
            if normalized["date"] is None:
                normalized["date"] = 0
            elif isinstance(normalized["date"], str):
                # Parse ISO format timestamp and convert to Unix timestamp
                dt = datetime.fromisoformat(normalized["date"].replace('Z', '+00:00'))
                normalized["date"] = int(dt.timestamp())
            elif not isinstance(normalized["date"], int):
                normalized["date"] = int(normalized["date"])

        return normalized

    def get_all(self) -> list[Posting]:
        
        """Get all postings from Supabase."""
        response = self.client.table(self.table_name).select("*").execute()

        return [Posting(**self._normalize_posting_data(posting_dict)) for posting_dict in response.data]

    def get_by_id(self, posting_id: str) -> Posting | None:
        """Get a posting by ID from Supabase."""
        response = self.client.table(self.table_name).select("*").eq("id", posting_id).execute()

        if response.data and len(response.data) > 0:
            return Posting(**self._normalize_posting_data(response.data[0]))
        return None

    def create(self, posting: Posting) -> Posting:
        """Create a new posting in Supabase."""
        # Convert Unix timestamp to ISO format for Supabase
        date_iso = None
        if posting.date > 0:
            date_iso = datetime.fromtimestamp(posting.date).isoformat()

        posting_dict = {
            "id": posting.id,
            "title": posting.title,
            "location": posting.location,
            "work_arrangement": posting.work_arrangement,
            "salary": posting.salary,
            "salary_type": posting.salary_type,
            "url": posting.url,
            "term": posting.term,
            "categories": posting.categories,
            "company": posting.company,
            "date": date_iso,
        }

        response = self.client.table(self.table_name).insert(posting_dict).execute()

        if response.data and len(response.data) > 0:
            return Posting(**self._normalize_posting_data(response.data[0]))
        return posting

    def bulk_delete(self, posting_ids: list[str], batch_size: int = 1000) -> int:
        """Delete multiple postings by IDs in batches."""
        total_deleted = 0

        for i in range(0, len(posting_ids), batch_size):
            batch = posting_ids[i:i + batch_size]
            response = self.client.table(self.table_name).delete().in_("id", batch).execute()
            total_deleted += len(response.data)

        return total_deleted
