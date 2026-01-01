"""
Test script to verify Supabase connectivity using PostingRepository.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.repository import PostingRepository

def test_supabase_connection():
    """
    Test Supabase connectivity by calling get_all() on PostingRepository.
    """
    print("="*60)
    print("SUPABASE CONNECTION TEST")
    print("="*60)
    print("\nInitializing PostingRepository...\n")

    try:
        # Initialize repository (tests connection)
        repo = PostingRepository()
        print("✓ Repository initialized successfully")

        # Test get_all method
        print("\nFetching all postings from Supabase...")
        postings = repo.get_all()

        print(f"\n{'='*60}")
        print(f"SUCCESS: Retrieved {len(postings)} posting(s)")
        print(f"{'='*60}\n")

        # Display postings if any exist
        if postings:
            print("Sample postings:\n")
            for i, posting in enumerate(postings[:5], 1):  # Show first 5
                print(posting)
                print()

            if len(postings) > 5:
                print(f"... and {len(postings) - 5} more posting(s)")
        else:
            print("No postings found in database (table is empty)")

        return True

    except ValueError as e:
        print(f"✗ Configuration Error: {e}")
        print("\nMake sure SUPABASE_URL and SUPABASE_KEY are set in .env file")
        return False

    except Exception as e:
        print(f"✗ Connection Error: {e}")
        print(f"\nError type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
