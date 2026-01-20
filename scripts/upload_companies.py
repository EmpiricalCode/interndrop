"""Script to upload companies from companies.json to Supabase."""

import json
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    # Load environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

    # Initialize Supabase client
    client = create_client(supabase_url, supabase_key)

    # Load companies from JSON
    config_path = Path(__file__).parent.parent / "src" / "shared" / "companies.json"
    with open(config_path) as f:
        data = json.load(f)

    companies = data["companies"]
    print(f"Found {len(companies)} companies to upload")

    # Upload each company
    for company in companies:
        company_dict = {
            "name": company["name"],
            "url": company["url"],
            "paged": company["paged"],
            "page_query_param": company["page_query_param"],
        }

        try:
            response = client.table("Companies").insert(company_dict).execute()
            print(f"✓ Uploaded: {company['name']}")
        except Exception as e:
            print(f"✗ Failed to upload {company['name']}: {e}")

    print(f"\nDone! Uploaded {len(companies)} companies to Supabase.")


if __name__ == "__main__":
    main()
