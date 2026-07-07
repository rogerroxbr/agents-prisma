"""Database configuration."""
import os
from urllib.parse import quote_plus


def get_database_url():
    """Build database connection URL from environment variables."""
    USE_SQLITE = os.getenv('USE_SQLITE', 'true').lower() == 'true'
    
    if USE_SQLITE:
        return "sqlite:///./prisma_test.db"
    else:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = int(os.getenv("DB_PORT", 5432))
        DB_NAME = os.getenv("DB_NAME", "prisma_dev")
        DB_USER = os.getenv("DB_USER", "postgres_user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "secure_password_123")
        
        return f"postgresql+asyncpg://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Default database URL (can be overridden by environment variable)
db_url = get_database_url()
