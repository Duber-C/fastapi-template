import argparse
import getpass
import os
from typing import Optional

from sqlmodel import Session

from src.core.database import engine
from src.modules.users.enums import RoleEnum
from src.modules.users.models.users import User
from src.modules.users.selectors import UserSelector


def create_admin(email: str, password: str) -> Optional[User]:
    with Session(engine) as session:
        new_user = User.model_validate(
            {
                "email": email,
                "password": password,
            }
        )

        try:
            user = UserSelector.create(new_user, session, [RoleEnum.superadmin])
            print(f"Created admin user {email}")
            return user
        except Exception as e:
            print('failed with error ', e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an admin user.")
    parser.add_argument(
        "-c",
        "--console",
        action="store_true",
        help="Prompt for credentials instead of using environment variables.",
    )
    args = parser.parse_args()

    if args.console:
        email = input('Email: ')

        while True:
            password = getpass.getpass('Password: ')
            re_password = getpass.getpass('Password: ')

            if password == re_password:
                break

            print('Paswords aren\'t the same')
    else:
        email = os.getenv('ADMIN_MAIL')
        password = os.getenv('ADMIN_PASSWORD')

    if not email or not password:
        print("Missing ADMIN_MAIL or ADMIN_PASSWORD.")
        return 1

    create_admin(email, password)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
