from db import users_collection
from models import UserBase, UserDetailsModel
from settings import get_logger, verify_password

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

    def get_user_info(self, username: str):
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
