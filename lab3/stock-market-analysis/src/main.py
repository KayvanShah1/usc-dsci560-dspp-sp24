import argparse
from datetime import datetime

import pandas as pd

from manager import InvalidUserException, PortfolioManager, TickerDataManager, UserManager
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
        raise InvalidUserException(
            "Invalid username or password. If you do not have an account try creating a new user."
        )


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


def fetch_stocks_data_portfolio(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio = portfolio_manager.get_portfolio_by_id(portfolio_id=args.portfolio_id)

        if portfolio:
            portfolio = portfolio.model_dump()
            for stocks in portfolio["tickers"]:
                ticker_data = TickerDataManager.get_stock_data(
                    ticker_code=stocks["ticker_code"],
                    start_date=(
                        datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
                    ),
                    end_date=(
                        datetime.strptime(args.end_date, "%Y-%m-%d")
                        if args.end_date
                        else datetime.utcnow()
                    ),
                )
                logger.info(pd.DataFrame(ticker_data))
    else:
        raise InvalidUserException("Invalid username or password")


def fetch_portfolio_by_id(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        portfolio_manager = PortfolioManager(username=args.username)
        portfolio = portfolio_manager.get_portfolio_by_id(portfolio_id=args.portfolio_id)
        if portfolio:
            logger.info(f"User's Portfolio:\n{pretty_repr(portfolio.model_dump())}")
    else:
        raise InvalidUserException("Invalid username or password")


###################################################################################################
# Ticker Data Management
###################################################################################################
def get_stock_market_data(args):
    user_manager = UserManager()
    is_verified = user_manager.verify_user(args.username, args.password)
    if is_verified:
        ticker_data = TickerDataManager.get_stock_data(
            ticker_code=args.ticker_code,
            start_date=datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None,
            end_date=(
                datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else datetime.utcnow()
            ),
        )
        logger.info(pd.DataFrame(ticker_data))
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

    # Subparser for the "fetch_portfolio_by_id" command
    fetch_portfolio_parser = portfolio_subparsers.add_parser(
        "fetch-one", help="Fetch one stock portfolio information by id"
    )
    fetch_portfolio_parser.add_argument("--username", type=str, required=True, help="Username")
    fetch_portfolio_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )
    fetch_portfolio_parser.add_argument(
        "--portfolio_id", type=str, required=True, help="Portfolio ID"
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

    # Subparser for the "fetch_stocks_data_portfolio" command
    fetch_portfolio_data_parser = portfolio_subparsers.add_parser(
        "fetch-portfolio-data", help="Fetch stocks data for a portfolio by id"
    )
    fetch_portfolio_data_parser.add_argument("--username", type=str, required=True, help="Username")
    fetch_portfolio_data_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )
    fetch_portfolio_data_parser.add_argument(
        "--portfolio_id", type=str, required=True, help="Portfolio ID"
    )
    fetch_portfolio_data_parser.add_argument(
        "--start_date", type=str, required=False, help="Start date", default=None
    )
    fetch_portfolio_data_parser.add_argument(
        "--end_date",
        type=str,
        required=False,
        help="End date",
        default=datetime.utcnow().strftime("%Y-%m-%d"),
    )

    ###############################################################################################
    # Create parser for the "market-data" command
    ###############################################################################################
    market_parser = subparsers.add_parser("market-data", help="Fetch market data commands")
    market_subparsers = market_parser.add_subparsers(
        dest="subcommand", help="Available subcommands"
    )

    # Subparser for the "add_stock" command
    fetch_stock_data_parser = market_subparsers.add_parser(
        "fetch-stock-data", help="Add a stock to a portfolio"
    )
    fetch_stock_data_parser.add_argument("--username", type=str, required=True, help="Username")
    fetch_stock_data_parser.add_argument(
        "--password", type=str, required=True, help="User's password"
    )
    fetch_stock_data_parser.add_argument(
        "--ticker_code", type=str, required=True, help="Ticker code"
    )
    fetch_stock_data_parser.add_argument(
        "--start_date", type=str, required=False, help="Start date", default=None
    )
    fetch_stock_data_parser.add_argument(
        "--end_date",
        type=str,
        required=False,
        help="End date",
        default=datetime.utcnow().strftime("%Y-%m-%d"),
    )

    ###############################################################################################
    # Parse the command-line arguments
    ###############################################################################################
    args = parser.parse_args()

    # Dispatch to the appropriate function based on the subcommand
    if args.command == "user":
        if args.subcommand == "create":
            create_user(args)
        elif args.subcommand == "get-info":
            get_user_info(args)
        else:
            logger.error("Invalid subcommand. Use 'create' or 'get-info'.")

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
        elif args.subcommand == "fetch-one":
            fetch_portfolio_by_id(args)
        elif args.subcommand == "fetch-portfolio-data":
            fetch_stocks_data_portfolio(args)
        else:
            logger.error(
                "Invalid portfolio subcommand. Use 'create', 'remove', 'add-stock', 'remove-stock',"
                " 'fetch-one' or 'list-all'."
            )

    if args.command == "market-data":
        if args.subcommand == "fetch-stock-data":
            get_stock_market_data(args)
        else:
            logger.error("Invalid subcommand. Use 'fetch-stock-data'.")


if __name__ == "__main__":
    main()
