"""Test SQLAlchemy database connectivity."""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os

# Build URL from environment variables (use 5433 for container mapping)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5433))  # Container maps to host port 5433
DB_NAME = os.getenv("DB_NAME", "prisma_dev")
DB_USER = os.getenv("DB_USER", "postgres_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secure_password_123")

url = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f'Connection URL: {url}')

engine = create_engine(url)
print('Engine created successfully!')

# Test actual connection
with engine.connect() as conn:
    result = conn.execute('SELECT version();')
    print(f"✓ PostgreSQL {result.fetchone()[0]} connected successfully!")
