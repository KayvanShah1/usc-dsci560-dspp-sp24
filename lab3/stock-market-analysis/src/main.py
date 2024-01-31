import argparse
from datetime import datetime

from manager import InvalidUserException, PortfolioManager, UserManager
from models import PortfolioModel, UserBase
from rich.pretty import pretty_repr
from settings import get_logger, get_password_hash

logger = get_logger(__name__)


###################################################################################################
# User Management
###################################################################################################
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
        user_info = user_manager.get_user_details(args.username)
        logger.info(f"User Information: {user_info.model_dump_json()}")
    else:
        raise InvalidUserException("Invalid username or password")


###################################################################################################
# Portfolio Management
###################################################################################################
def create_portfolio(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio_manager.create_portfolio(
            PortfolioModel(
                username=args.username,
                portfolio_name=args.portfolio_name,
                created_at=datetime.utcnow(),
            )
        )
    else:
        raise InvalidUserException("Invalid username or password")


def remove_portfolio(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio_manager.remove_portfolio(portfolio_id=args.portfolio_id)
    else:
        raise InvalidUserException("Invalid username or password")


def add_stock(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio_manager.add_stock(ticker_code=args.ticker_code, portfolio_id=args.portfolio_id)
    else:
        raise InvalidUserException("Invalid username or password")


def remove_stock(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio_manager.remove_stock(ticker_code=args.ticker_code, portfolio_id=args.portfolio_id)
    else:
        raise InvalidUserException("Invalid username or password")


def list_all_portfolios(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolios = portfolio_manager.get_portfolios()
        if portfolios:
            logger.info(f"User's Portfolios:\n{pretty_repr(portfolios.model_dump())}")
        else:
            logger.info("No portfolios found")
    else:
        raise InvalidUserException("Invalid username or password")


###################################################################################################
# Command Line Toolkit
###################################################################################################
def main():
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Command-line interface for Stock Market Analysis Application"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    ###############################################################################################
    # Create parser for the "user" command
    ###############################################################################################
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

    ###############################################################################################
    # Create parser for the "portfolio" command
    ###############################################################################################
    portfolio_parser = subparsers.add_parser("portfolio", help="Portfolio management commands")
    portfolio_subparsers = portfolio_parser.add_subparsers(
        dest="subcommand", help="Available subcommands"
    )

    # Subparser for the "create" command
    create_portfolio_parser = portfolio_subparsers.add_parser(
        "create", help="Create a new portfolio"
    )
    create_portfolio_parser.add_argument("--username", type=str, required=True, help="Username")
    create_portfolio_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )
    create_portfolio_parser.add_argument(
        "--portfolio_name", type=str, required=True, help="Portfolio name"
    )

    # Subparser for the "remove" command
    remove_portfolio_parser = portfolio_subparsers.add_parser("remove", help="Remove a portfolio")
    remove_portfolio_parser.add_argument("--username", type=str, required=True, help="Username")
    remove_portfolio_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )
    remove_portfolio_parser.add_argument(
        "--portfolio_id", type=str, required=True, help="Portfolio ID"
    )

    # Subparser for the "list_all_portfolios" command
    list_all_portfolios_parser = portfolio_subparsers.add_parser(
        "list-all", help="List all stock portfolios for a user"
    )
    list_all_portfolios_parser.add_argument("--username", type=str, required=True, help="Username")
    list_all_portfolios_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )

    # Subparser for the "add_stock" command
    add_stock_parser = portfolio_subparsers.add_parser(
        "add-stock", help="Add a stock to a portfolio"
    )
    add_stock_parser.add_argument("--username", type=str, required=True, help="Username")
    add_stock_parser.add_argument("--password", type=str, required=True, help="User's password")
    add_stock_parser.add_argument("--ticker_code", type=str, required=True, help="Ticker code")
    add_stock_parser.add_argument("--portfolio_id", type=str, required=True, help="Portfolio ID")

    # Subparser for the "remove_stock" command
    add_stock_parser = portfolio_subparsers.add_parser(
        "remove-stock", help="Remove a stock from a portfolio"
    )
    add_stock_parser.add_argument("--username", type=str, required=True, help="Username")
    add_stock_parser.add_argument("--password", type=str, required=True, help="User's password")
    add_stock_parser.add_argument("--ticker_code", type=str, required=True, help="Ticker code")
    add_stock_parser.add_argument("--portfolio_id", type=str, required=True, help="Portfolio ID")

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

    # Dispatch to the appropriate function based on the subcommand
    if args.command == "portfolio":
        if args.subcommand == "create":
            create_portfolio(args)
        elif args.subcommand == "remove":
            remove_portfolio(args)
        elif args.subcommand == "add-stock":
            add_stock(args)
        elif args.subcommand == "remove-stock":
            remove_stock(args)
        elif args.subcommand == "list-all":
            list_all_portfolios(args)
        else:
            logger.error(
                "Invalid portfolio subcommand. Use 'create', 'remove', 'add-stock', 'remove-stock',"
                " or 'list-all'."
            )


if __name__ == "__main__":
    main()
