from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from settings import config


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
    try:
        client = AsyncIOMotorClient(config.MONGODB_URI)
    except Exception:
        print("""Unable to connect to Async Mongo Motor... Connecting to standard Motor""")
        client = MongoClient(config.MONGODB_URI)
except Exception as e:
    print("Unable to connect to MongoDB client: %s" % e)

# Create DB cursors
main_db = client["yf_panels"]
ticker_db = client["yf_stock_tickers"]

# Get collections

users_collection = get_collection(main_db, "users")
# Add unique index to the "username.root" field
users_collection.create_index([("username", 1)], unique=True)

portfolios_collection = get_collection(main_db, "portfolios")
