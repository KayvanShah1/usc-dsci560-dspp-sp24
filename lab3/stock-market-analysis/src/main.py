import argparse
from datetime import datetime

from manager import UserManager, InvalidUserException
from models import UserBase
from settings import get_password_hash, get_logger

logger = get_logger(__name__)


def create_user(args):
    user_manager = UserManager()
    user_manager.create_user(
        UserBase(
            username=args.username,
            name={"first_name": args.first_name, "last_name": args.last_name},
            password=get_password_hash(args.password),
            created_at=datetime.utcnow(),
        )
    )


def get_user_info(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        user_info = user_manager.get_user_info(args.username)
        logger.info(f"User Information: {user_info.model_dump_json()}")
    else:
        raise InvalidUserException("Invalid username or password")


def main():
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Command-line interface for Stock Market Analysis Application"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create parser for the "user" command
    user_parser = subparsers.add_parser("user", help="User management commands")
    user_subparsers = user_parser.add_subparsers(
        dest="subcommand", help="Available user management subcommands"
    )

    # Subparser for the "create" command
    create_parser = user_subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("--username", type=str, required=True, help="Username")
    create_parser.add_argument("--first_name", type=str, required=True, help="User's first name")
    create_parser.add_argument("--last_name", type=str, required=True, help="User's last name")
    create_parser.add_argument("--password", type=str, required=True, help="User's password")

    # Subparser for the "get" command
    get_parser = user_subparsers.add_parser("get-info", help="Get user information")
    get_parser.add_argument("--username", type=str, required=True, help="Username")
    get_parser.add_argument("--password", type=str, required=True, help="User's password")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Dispatch to the appropriate function based on the subcommand
    if args.command == "user":
        if args.subcommand == "create":
            create_user(args)
        elif args.subcommand == "get-info":
            get_user_info(args)
        else:
            logger.error("Invalid subcommand. Use 'create' or 'get-info'.")


if __name__ == "__main__":
    main()
