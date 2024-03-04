import logging
import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(curr_file_dir)
    root_dir = os.path.dirname(app_dir)

    env_file = os.path.join(app_dir, ".env")
    templates_dir = os.path.join(app_dir, "templates")
    static_dir = os.path.join(app_dir, "assets")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8")

    # Database configuration
    MYSQL_USERNAME: str = Field()
    MYSQL_PASSWORD: str = Field()
    MYSQL_HOST: str = Field()
    MYSQL_PORT: str = Field()
    MYSQL_DB_NAME: str = Field()

    USER_AGENT: str = Field(default="Oil Wells Viz. Bot")

    PROJECT_NAME: str = Field(default="Oil Wells Analysis and Visualization Project")

    BACKEND_CORS_ORIGINS: list = Field(default=["*"])
    STATIC_ROOT: str = Field(default=Path.static_dir)


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
