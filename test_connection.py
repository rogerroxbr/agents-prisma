import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os

password = os.getenv('DB_PASSWORD') or ''
url = f"postgresql://{os.getenv('DB_USER')}:{quote_plus(password)}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
print(f"Connection URL: {url}")

engine = create_engine(url)
with engine.connect() as conn:
    result = conn.execute(text('SELECT version();'))
    print(f"OK PostgreSQL {result.fetchone()[0]} connected successfully!")
