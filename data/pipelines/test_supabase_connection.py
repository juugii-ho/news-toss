import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env.local
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.local'))

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.error("Supabase credentials are not set in environment variables.")
        raise ValueError("Supabase credentials missing.")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def test_connection():
    logger.info("Attempting to test Supabase connection...")
    try:
        supabase: Client = get_supabase_client()
        logger.info("Supabase client created successfully.")

        # Try a very simple query
                # Use getattr to bypass potential parser confusion with the 'from' keyword
        response = getattr(supabase, 'from')('MVP2_articles').select('*').limit(1).execute()
        
        logger.info(f"Successfully executed a simple query. Data: {response.data}")
        logger.info("Supabase connection test successful!")
    except Exception as e:
        logger.error(f"Supabase connection test FAILED: {e}")

if __name__ == "__main__":
    test_connection()
