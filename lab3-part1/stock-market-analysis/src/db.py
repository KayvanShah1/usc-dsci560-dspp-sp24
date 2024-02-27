from typing import Any

from bson import ObjectId
from pydantic_core import core_schema
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

    # @classmethod
    # def __modify_schema__(cls, field_schema):
    #     field_schema.update(type="string")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda x: str(x)),
        )


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
users_collection.create_index([("username", 1)], unique=True)

tickers_info_collection = get_collection(main_db, "tickers_info")
tickers_info_collection.create_index([("ticker_code", 1)], unique=True)

portfolios_collection = get_collection(main_db, "portfolios")
portfolios_collection.create_index([("portfolio_name", 1)], unique=True)