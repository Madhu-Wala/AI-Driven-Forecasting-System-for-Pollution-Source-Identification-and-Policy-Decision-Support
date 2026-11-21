import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_auth_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor,
        connect_timeout=10
    )


def create_users_table():
    query = """
    CREATE TABLE IF NOT EXISTS public.users (
        id BIGSERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role VARCHAR(30) NOT NULL
            CHECK (role IN ('citizen', 'policy_maker')),
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower
        ON public.users (LOWER(username))
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_lower
        ON public.users (LOWER(email))
    """)

    connection = get_auth_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()