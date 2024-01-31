from datetime import datetime

from db import PyObjectId, portfolios_collection, tickers_info_collection, users_collection
from models import (
    PortfolioListModel,
    PortfolioModel,
    PortfolioPreviewModel,
    UserBase,
    UserDetailsModel,
)
from settings import get_logger, verify_password
from yf import get_ticker_info

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
            portfolio_name = portfolio.get("portfolio_name", "")

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


class TickerDataManager:
    None


pm = PortfolioManager(username="john_doe")

# p1 = pm.create_portfolio(
#     PortfolioModel(
#         username=pm.username,
#         portfolio_name="portfolio198",
#         # tickers: Optional[List[TickerSummaryModel]] = None
#         created_at=datetime.utcnow(),
#     )
# )

# p2 = pm.create_portfolio(
#     PortfolioModel(
#         username=pm.username,
#         portfolio_name="portfolio2",
#         # tickers: Optional[List[TickerSummaryModel]] = None
#         created_at=datetime.utcnow(),
#     )
# )

# p3 = pm.create_portfolio(
#     PortfolioModel(
#         username=pm.username,
#         portfolio_name="portfolio3",
#         # tickers: Optional[List[TickerSummaryModel]] = None
#         created_at=datetime.utcnow(),
#     )
# )

# pm.add_stock("AAPL", "65ba1f98a59d90bf7bb83d98")
# pm.add_stock("AADI", "65ba1ff4bc2652f71f8f5ae4")
# pm.add_stock("ADANIPORTS.NS", "65ba1ff4bc2652f71f8f5ae4")
# # pm.remove_stock("AADI", "65ba0a9fe4178f1bf53babaa")

# p = pm.get_portfolios()
# print(p.model_dump())
