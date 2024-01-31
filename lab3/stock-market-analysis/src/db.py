from bson import ObjectId

from pymongo import MongoClient
from settings import config, get_logger

logger = get_logger(__name__)


# BSON and JSON compatibility addressed here
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def get_collection(db, collection_name: str):
    return db[collection_name]


try:
    client = MongoClient(config.MONGODB_URI)
except Exception as e:
    logger.error("Unable to connect to MongoDB client: %s" % e)

# Create DB cursors
main_db = client["yf_panels"]
ticker_db = client["yf_stock_ticker_data"]

# Get collections

users_collection = get_collection(main_db, "users")
# Add unique index to the "username.root" field
users_collection.create_index([("username", 1)], unique=True)

tickers_collection = get_collection(main_db, "tickers")
tickers_collection.create_index([("ticker_code", 1)], unique=True)

portfolios_collection = get_collection(main_db, "portfolios")
