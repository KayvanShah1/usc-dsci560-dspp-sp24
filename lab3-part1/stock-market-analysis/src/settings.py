import logging
import os
from functools import lru_cache

from passlib.context import CryptContext
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(curr_file_dir)
    env_file = os.path.join(root_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8"
    )

    MONGODB_URI: str = Field()
    YFINANCE_CACHE_FILE: str = Field(
        default=os.path.relpath(os.path.join(Path.root_dir, "yfinance.cache"))
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def get_logger(name):
    # Create a logger
    logger = logging.getLogger(name)

    # Set the logging level (adjust as needed)
    logger.setLevel(logging.DEBUG)

    # Create a console handler and set the level
    ch = RichHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    return logger


@lru_cache
def get_settings():
    return Settings()


config = get_settings()
