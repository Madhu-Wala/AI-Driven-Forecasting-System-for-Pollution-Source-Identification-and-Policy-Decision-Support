import getpass
import re

from app.models.user import (
    create_users_table,
    get_auth_db_connection
)
from app.auth.security import hash_password


def main():
    create_users_table()

    print("\nVayuSuchak - Create User")
    print("Available roles: citizen, policy_maker\n")

    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()
    role = input("Role: ").strip().lower()

    if not username or not email:
        print("Username and email are required.")
        return

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        print("Enter a valid email address.")
        return

    if role not in ("citizen", "policy_maker"):
        print("Invalid role.")
        return

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if len(password) < 12:
        print("Password must contain at least 12 characters.")
        return

    if password != confirm_password:
        print("Passwords do not match.")
        return

    password_hash = hash_password(password)
    connection = get_auth_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO public.users
                    (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (username, email, password_hash, role)
            )

            user = cursor.fetchone()

        connection.commit()
        print(f"\nUser created successfully. User ID: {user['id']}")

    except Exception as error:
        connection.rollback()

        if getattr(error, "pgcode", None) == "23505":
            print("Username or email already exists.")
        else:
            raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()