import os
import secrets

from dotenv import load_dotenv
from psycopg2.errors import UniqueViolation

from app.auth.database import get_auth_connection
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

load_dotenv()


def create_policy_maker(data):
    configured_code = os.getenv("POLICY_SIGNUP_INVITE_CODE")

    if not configured_code:
        raise RuntimeError(
            "POLICY_SIGNUP_INVITE_CODE is missing from backend .env"
        )

    if not secrets.compare_digest(
        data.invitation_code,
        configured_code
    ):
        return None, "Invalid invitation code"

    connection = get_auth_connection()

    try:
        with connection.cursor() as cursor:
            password_hash = hash_password(data.password)

            cursor.execute(
                """
                INSERT INTO public.users
                    (full_name, username, email, password_hash, role)
                VALUES (%s, %s, %s, %s, 'policy_maker')
                RETURNING id, full_name, username, email, role
                """,
                (
                    data.full_name.strip(),
                    data.username.strip().lower(),
                    str(data.email).lower(),
                    password_hash
                )
            )

            user = cursor.fetchone()

        connection.commit()

        user["id"] = int(user["id"])
        token = create_access_token(user["id"])

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": dict(user)
        }, None

    except UniqueViolation:
        connection.rollback()
        return None, "Username or email is already registered"

    finally:
        connection.close()


def authenticate_user(identifier: str, password: str):
    connection = get_auth_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, username, email,
                       password_hash, role, is_active
                FROM public.users
                WHERE LOWER(username) = LOWER(%s)
                   OR LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (identifier.strip(), identifier.strip())
            )

            user = cursor.fetchone()

        if not user:
            return None

        if not user["is_active"]:
            return None

        if user["role"] != "policy_maker":
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        user_id = int(user["id"])

        return {
            "access_token": create_access_token(user_id),
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "full_name": user["full_name"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
        }

    finally:
        connection.close()


def get_user_by_id(user_id: int):
    connection = get_auth_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, full_name, username, email, role, is_active
                FROM public.users
                WHERE id = %s
                LIMIT 1
                """,
                (user_id,)
            )

            user = cursor.fetchone()

        if not user or not user["is_active"]:
            return None

        user["id"] = int(user["id"])
        return dict(user)

    finally:
        connection.close()