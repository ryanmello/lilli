from supabase import create_client, Client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class SupabaseService:
    _client: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        """Get or create the Supabase client singleton."""
        if cls._client is None:
            if not settings.SUPABASE_PROJECT_URL or not settings.SUPABASE_SECRET_API_KEY:
                raise ValueError(
                    "Supabase credentials not configured. "
                    "Please set SUPABASE_PROJECT_URL and SUPABASE_SECRET_API_KEY in your .env file."
                )
            
            cls._client = create_client(
                settings.SUPABASE_PROJECT_URL,
                settings.SUPABASE_SECRET_API_KEY
            )
            logger.info("Supabase client initialized")
        
        return cls._client

    @classmethod
    def table(cls, table_name: str):
        """Get a table reference for querying."""
        return cls.get_client().table(table_name)


# Convenience function for direct access
def get_supabase() -> Client:
    """Get the Supabase client instance."""
    return SupabaseService.get_client()


supabase = SupabaseService()
