"""
Database initialization helpers.

Run after applying migrations to seed the first system administrator:

    python -m app.database.init_db

The super admin credentials can be customized through environment
variables:
    SUPER_ADMIN_NAME
    SUPER_ADMIN_EMAIL
    SUPER_ADMIN_PASSWORD
"""

import os

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

DEFAULT_ADMIN_NAME = "System Administrator"
DEFAULT_ADMIN_EMAIL = "admin@kyhc.local"
DEFAULT_ADMIN_PASSWORD = "changeme123"


def create_super_admin(
    full_name: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> User | None:
    """
    Create the initial super admin account if it does not exist.
    """

    full_name = (
        full_name
        or os.getenv("SUPER_ADMIN_NAME")
        or DEFAULT_ADMIN_NAME
    )

    email = (
        email
        or os.getenv("SUPER_ADMIN_EMAIL")
        or DEFAULT_ADMIN_EMAIL
    )

    password = password or os.getenv("SUPER_ADMIN_PASSWORD")

    using_default_password = password is None

    if using_default_password:
        password = DEFAULT_ADMIN_PASSWORD

    db = SessionLocal()

    try:
        existing = UserRepository.get_by_email(db, email)

        if existing:
            print(f"Super admin already exists: {email}")
            return existing

        admin = User(
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.SUPER_ADMIN,
        )

        admin = UserRepository.create(db, admin)

        if using_default_password:
            print(
                "Super admin created with the built-in default password:\n"
                f"  email:    {email}\n"
                f"  password: {password}\n"
                "Change the password after the first login."
            )
        else:
            print(
                "Super admin created:\n"
                f"  email:    {email}\n"
                "  password: (read from SUPER_ADMIN_PASSWORD)"
            )

        return admin

    finally:
        db.close()


if __name__ == "__main__":
    create_super_admin()
