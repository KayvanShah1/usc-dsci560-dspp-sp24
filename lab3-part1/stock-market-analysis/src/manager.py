from datetime import datetime, timedelta

import pymongo
from db import (
    PyObjectId,
    portfolios_collection,
    ticker_db,
    tickers_info_collection,
    users_collection,
)
from models import (
    PortfolioListModel,
    PortfolioModel,
    PortfolioPreviewModel,
    TickerDataModel,
    TickerInfoUpdateModel,
    TickerSummaryModel,
    UserBase,
    UserDetailsModel,
)
from settings import get_logger, verify_password
from yf import basic_preprocess, clean_ticker_data, get_ticker_data, get_ticker_info, resample

logger = get_logger(__name__)


class DuplicateUsernameError(ValueError):
    pass


class InvalidUserException(ValueError):
    pass


class UserManager:
    def __init__(self, users_collection=users_collection):
        self.users_collection = users_collection

    def create_user(self, user_data: UserBase):
        user_data = user_data.model_dump()
        # Check if the username is unique
        existing_user = self.users_collection.find_one(
            {"username": user_data["username"]}, {"_id": 0}
        )
        if existing_user:
            raise DuplicateUsernameError("Username already exists")

        # Create a new user
        new_user = UserBase(**user_data)
        new_user = self.users_collection.insert_one(new_user.model_dump())
        created_user = self.users_collection.find_one({"_id": new_user.inserted_id}, {"_id": 0})
        logger.info(f"Created user with username: {user_data['username']} successfully.")
        return UserDetailsModel(**created_user)

    def get_user_details(self, username: str):
        user = self.users_collection.find_one({"username": username}, {"_id": 0})
        if user:
            return UserDetailsModel(**user)
        else:
            raise ValueError("User not found")

    def verify_user(self, username: str, password):
        user = self.users_collection.find_one({"username": username}, {"_id": 0})
        if user and verify_password(password, user["password"]):
            logger.info("User verification successful")
            return True
        else:
            return False


class PortfolioManager:
    def __init__(self, username: str, portfolios_collection=portfolios_collection):
        self.username = username
        self.portfolios_collection = portfolios_collection

    def create_portfolio(self, portfolio_data: PortfolioModel):
        portfolio_data = portfolio_data.model_dump()
        curr = self.portfolios_collection.find_one(
            {"portfolio_name": portfolio_data["portfolio_name"]}, {"_id": 0}
        )
        if curr:
            logger.exception(
                f"Portfolio cannot have the same name: '{portfolio_data['portfolio_name']}'. Please"
                " use a different name"
            )
        else:
            new_portfolio = self.portfolios_collection.insert_one(portfolio_data)
            created_portfolio = self.portfolios_collection.find_one(
                {"_id": new_portfolio.inserted_id}
            )
            logger.info(
                f"Created portfolio with name: '{created_portfolio['portfolio_name']}' and"
                f" portfolio _id: '{new_portfolio.inserted_id}' successfully."
            )
            return PortfolioPreviewModel(**created_portfolio)

    def get_portfolios(self):
        portfolios = self.portfolios_collection.find({"username": self.username})
        portfolios_list = list(portfolios)
        return PortfolioListModel(portfolios_list)

    def get_portfolio_by_id(self, portfolio_id: str):
        portfolio = self.portfolios_collection.find_one(
            {"username": self.username, "_id": PyObjectId(portfolio_id)}
        )
        if portfolio:
            return PortfolioPreviewModel(**portfolio)
        else:
            logger.error(
                f"Portfolio with id '{portfolio_id}' not found. Please retry with correct id."
            )

    def add_stock(self, ticker_code: str, portfolio_id: str):
        portfolio = self.portfolios_collection.find_one(
            {"username": self.username, "_id": PyObjectId(portfolio_id)}, {"_id": 0}
        )
        if portfolio:
            tickers = [] if portfolio["tickers"] is None else portfolio["tickers"]
            if any(ticker["ticker_code"] == ticker_code for ticker in tickers):
                logger.warning(
                    f"Ticker {ticker_code} is already present in the "
                    f"'{portfolio['portfolio_name']}'. Cannot be added again."
                )
                return

            ticker_info = TickerInfoManager.get_ticker_details(ticker_code)
            tickers.append(ticker_info)

            # Update the portfolio with the new tickers list
            self.portfolios_collection.update_one(
                {"_id": PyObjectId(portfolio_id)},
                {"$set": {"tickers": tickers, "updated_at": datetime.utcnow()}},
            )

            logger.info(f"Sucessfully added {ticker_code} to '{portfolio['portfolio_name']}'.")
        else:
            logger.error(f"Invalid portfolio id: {portfolio_id}")

    def remove_stock(self, ticker_code: str, portfolio_id: str):
        portfolio = self.portfolios_collection.find_one(
            {"username": self.username, "_id": PyObjectId(portfolio_id)}, {"_id": 0}
        )
        if portfolio:
            # Get or initialize the "tickers" field in the portfolio
            tickers = [] if portfolio["tickers"] is None else portfolio["tickers"]

            # Check if the ticker is present in the portfolio
            if any(ticker["ticker_code"] == ticker_code for ticker in tickers):
                # Remove the ticker from the list
                tickers = [ticker for ticker in tickers if ticker["ticker_code"] != ticker_code]

                # Update the portfolio with the new tickers list
                self.portfolios_collection.update_one(
                    {"_id": PyObjectId(portfolio_id)},
                    {"$set": {"tickers": tickers, "updated_at": datetime.utcnow()}},
                )

                logger.info(
                    f"Successfully removed '{ticker_code}' from '{portfolio['portfolio_name']}'."
                )
            else:
                logger.warning(f"Ticker '{ticker_code}' not found in the portfolio.")
        else:
            logger.error(f"Invalid portfolio id: {portfolio_id}")

    def remove_portfolio(self, portfolio_id: str):
        portfolio = self.portfolios_collection.find_one(
            {"username": self.username, "_id": PyObjectId(portfolio_id)}
        )

        if portfolio:
            portfolio_name = portfolio["portfolio_name"]

            # Remove the portfolio
            self.portfolios_collection.delete_one({"_id": PyObjectId(portfolio_id)})

            logger.info(f"Successfully removed portfolio '{portfolio_name}'.")
        else:
            logger.error(f"Invalid portfolio id: '{portfolio_id}'")


class TickerInfoManager:
    @staticmethod
    def get_ticker_details(ticker_code: str):
        t_info = tickers_info_collection.find_one(
            {"ticker_code": ticker_code}, {"_id": 0, "created_at": 0}
        )
        if not t_info:
            logger.info(
                "Ticker code not found in the info collection. Querying the Yahoo Finance service."
            )
            t_info = get_ticker_info(ticker_code)
            t_info["created_at"] = datetime.utcnow()
            tickers_info_collection.insert_one(t_info)
        return t_info

    @staticmethod
    def update_ticker_details(ticker_code: str):
        ticker_update_data = TickerInfoUpdateModel(updated_at=datetime.utcnow())
        result = tickers_info_collection.update_one(
            {"ticker_code": ticker_code}, {"$set": ticker_update_data.model_dump()}
        )
        # Verify the update was successful
        if result.modified_count > 0:
            updated_ticker = tickers_info_collection.find_one({"ticker_code": ticker_code})
            updated_ticker = TickerSummaryModel(**updated_ticker)
            logger.info(
                f"Updated ticker details for '{ticker_code}': {updated_ticker.model_dump()}"
            )


class TickerDataManager:
    @staticmethod
    def get_stock_data(
        ticker_code: str,
        start_date: datetime = None,
        end_date: datetime = datetime.utcnow(),
    ):
        ticker_info = TickerInfoManager.get_ticker_details(ticker_code)
        ticker_data_collection = ticker_db[ticker_info["ticker_code"]]

        logger.info(
            f"Fetching data for stock '{ticker_info['name']} ({ticker_info['ticker_code']})'"
        )

        ticker_data_collection.create_index([("datetime", pymongo.ASCENDING)], unique=True)
        try:
            # Check if ticker_data_collection has data
            if ticker_data_collection.count_documents({}) > 0:
                # Get the most recent date in the data
                most_recent_date = ticker_data_collection.find_one(
                    {},
                    sort=[("datetime", pymongo.DESCENDING)],
                    projection={"datetime": True},
                )

                most_historical_date = ticker_data_collection.find_one(
                    {},
                    sort=[("datetime", pymongo.ASCENDING)],
                    projection={"datetime": True},
                )

                if most_recent_date:
                    most_recent_date = most_recent_date["datetime"]

                    if (end_date.date() - most_recent_date.date()).days > 0:
                        logger.info(
                            f"Fetching additional data for '{ticker_code}' from"
                            f" {most_recent_date + timedelta(days=1)} to {end_date}."
                        )
                        additional_data = get_ticker_data(
                            ticker_info["ticker_code"],
                            start_date=most_recent_date + timedelta(days=1),
                            end_date=end_date,
                        )

                        if not additional_data.empty:
                            additional_data = clean_ticker_data(additional_data)
                            additional_data = resample(additional_data)
                            additional_data = basic_preprocess(additional_data)
                            additional_data = TickerDataModel(
                                data=additional_data.to_dict("records")
                            )

                            # Ingest data into the database
                            ticker_data_collection.insert_many(additional_data.model_dump()["data"])
                    else:
                        logger.debug(
                            f"No additional data needed for '{ticker_code}'. Most recent data is up"
                            " to date. Fetching data from the database."
                        )

                if most_historical_date:
                    most_historical_date = most_historical_date["datetime"]

                    if start_date is None:
                        comparator = datetime.strptime("1600-01-01", "%Y-%m-%d")
                        diff = most_historical_date.date() - comparator.date()
                    else:
                        diff = most_historical_date.date() - start_date.date()

                    if diff.days > 0:
                        logger.info(
                            f"Fetching old historical data for '{ticker_code}' from"
                            f" {start_date} to {most_historical_date - timedelta(days=1)}."
                        )
                        additional_data = get_ticker_data(
                            ticker_info["ticker_code"],
                            start_date=start_date,
                            end_date=most_historical_date - timedelta(days=1),
                        )

                        if not additional_data.empty:
                            additional_data = clean_ticker_data(additional_data)
                            additional_data = resample(additional_data)
                            additional_data = basic_preprocess(additional_data)
                            additional_data = TickerDataModel(
                                data=additional_data.to_dict("records")
                            )

                            # Ingest data into the database
                            ticker_data_collection.insert_many(additional_data.model_dump()["data"])
                    else:
                        logger.debug(
                            f"No old historical data needed for '{ticker_code}'. Most recent data"
                            " is up to date. Fetching data from the database."
                        )

            else:
                logger.warning(
                    f"Most recent date not found in '{ticker_code}' data collection. Fetching"
                    " full data."
                )
                # Fetch data based on the user's request
                df = get_ticker_data(
                    ticker_info["ticker_code"], start_date=start_date, end_date=end_date
                )
                df = clean_ticker_data(df)
                df = resample(df)
                df = basic_preprocess(df)

                df = TickerDataModel(data=df.to_dict("records"))

                # Ingest data into the database
                ticker_data_collection.insert_many(df.model_dump()["data"])

                logger.info(f"Fetched data for '{ticker_code}'. Most recent data is updated.")

                # Update ticker_info with the latest update time
                TickerInfoManager.update_ticker_details(ticker_info["ticker_code"])

            date_query = {"datetime": {"$lte": end_date}}
            if start_date is not None:
                date_query["datetime"]["$gte"] = start_date

            ticker_data = ticker_data_collection.find(date_query, {"_id": 0})

            return list(ticker_data)

        except Exception as e:
            logger.exception(f"Error processing ticker data: '{ticker_code}'. {e}")
