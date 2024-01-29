from models import UserSummaryModel, UserBase


class UserManager:
    def __init__(self, users_collection):
        self.users_collection = users_collection

    def create_user(self, user_data: dict):
        # Check if the username is unique
        existing_user = self.users_collection.find_one(
            {"username.root": user_data["username"]["root"]}
        )
        if existing_user:
            raise ValueError("Username is not unique")

        # Create a new user
        user = UserBase(**user_data)
        result = self.users_collection.insert_one(user.model_dump())
        return str(result.inserted_id)

    def get_user_info(self, username_root: str):
        user = self.users_collection.find_one({"username": username_root})
        if user:
            return UserSummaryModel(**user)
        else:
            raise ValueError("User not found")

    def verify_user(self, username_root: str):
        user = self.users_collection.find_one({"username": username_root})
        return user is not None
