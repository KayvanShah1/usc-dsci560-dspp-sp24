import logging
import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(curr_file_dir)
    root_dir = os.path.dirname(package_dir)

    env_file = os.path.join(package_dir, ".env")
    data_dir = os.path.join(root_dir, "data")
    data_text_dir = os.path.join(data_dir, "raw-text")

    gcp_service_account_key = os.path.join(package_dir, "test-5681a-202ae82505a3.json")

    if not os.path.exists(data_text_dir):
        os.makedirs(data_text_dir)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8")

    # Database configuration
    MYSQL_USERNAME: str = Field()
    MYSQL_PASSWORD: str = Field()
    MYSQL_HOST: str = Field()
    MYSQL_PORT: str = Field()
    MYSQL_DB_NAME: str = Field()

    USER_AGENT: str = Field(default="Oil Wells Data Scraper Bot")

    DRILLING_EDGE_BASE_URL: str = "https://www.drillingedge.com"
    DRILLING_EDGE_BASE_SEARCH_URL: str = f"{DRILLING_EDGE_BASE_URL}/search"

    GDRIVE_DATA_FOLDER_ID: str = Field(default="12g-bhOylyaMoLF5djocnAeZHBx-gsxgY")


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
