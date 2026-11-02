import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_database_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg2.connect(
        database_url,
        connect_timeout=10
    )