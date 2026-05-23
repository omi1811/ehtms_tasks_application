from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402


DEFAULT_USERNAME = "superuser"
DEFAULT_EMAIL = "superuser@ehtms.com"
DEFAULT_PASSWORD = "March@2024"
USER_ROLES = ("super_admin", "org_admin", "manager", "worker")
DEFAULT_ROLE = "super_admin"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed an EHTMS user.")
    parser.add_argument("--username", default=os.getenv("SEED_USER_USERNAME", DEFAULT_USERNAME))
    parser.add_argument("--email", default=os.getenv("SEED_USER_EMAIL", DEFAULT_EMAIL))
    parser.add_argument("--password", default=os.getenv("SEED_USER_PASSWORD", DEFAULT_PASSWORD))
    parser.add_argument(
        "--role",
        default=os.getenv("SEED_USER_ROLE", DEFAULT_ROLE),
        choices=USER_ROLES,
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL") or settings.DATABASE_URL,
        help="Overrides DATABASE_URL from the environment/.env file.",
    )
    return parser.parse_args()


def seed_user(args: argparse.Namespace) -> None:
    database_url = args.database_url.strip()
    engine = create_engine(database_url)

    with engine.begin() as connection:
        matches = connection.execute(
            text(
                """
                SELECT id, email, username
                FROM users
                WHERE email = :email OR username = :username
                """
            ),
            {"email": args.email, "username": args.username},
        ).mappings().all()

        if len({user["id"] for user in matches}) > 1:
            raise RuntimeError(
                "Cannot seed user because username and email belong to different users."
            )

        params = {
            "username": args.username,
            "email": args.email,
            "hashed_password": get_password_hash(args.password),
            "role": args.role,
        }

        if matches:
            connection.execute(
                text(
                    """
                    UPDATE users
                    SET username = :username,
                        email = :email,
                        hashed_password = :hashed_password,
                        role = :role,
                        is_active = true
                    WHERE id = :id
                    """
                ),
                {**params, "id": matches[0]["id"]},
            )
            action = "Updated"
        else:
            connection.execute(
                text(
                    """
                    INSERT INTO users (
                        username,
                        email,
                        hashed_password,
                        role,
                        is_active,
                        created_at
                    )
                    VALUES (
                        :username,
                        :email,
                        :hashed_password,
                        :role,
                        true,
                        now()
                    )
                    """
                ),
                params,
            )
            action = "Created"

        print(f"{action} user: {args.email} ({args.role})")


def main() -> None:
    args = parse_args()
    seed_user(args)


if __name__ == "__main__":
    main()
