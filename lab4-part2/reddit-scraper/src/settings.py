import logging
import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.logging import RichHandler


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(curr_file_dir)
    env_file = os.path.join(root_dir, ".env")
    ca_cert_file = os.path.join(root_dir, "ca.pem")
    models_dir = os.path.join(root_dir, "models")

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    embeddings_model = os.path.join(models_dir, "reddit_post_embeddings")
    clustering_model = os.path.join(models_dir, "post_clustering.pkl")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8")

    REDDIT_USERNAME: str = Field()
    REDDIT_PRAW_API_CLIENT_ID: str = Field()
    REDDIT_PRAW_API_CLIENT_SECRET_KEY: str = Field()

    USER_AGENT: str = Field(default="Reddit Bot")

    REDDIT_BASE_URL: str = Field(default="https://www.reddit.com/")

    MYSQL_USERNAME: str = Field()
    MYSQL_PASSWORD: str = Field()
    MYSQL_HOST: str = Field()
    MYSQL_PORT: str = Field()

    RANDOM_STATE: int = Field(default=42)
    OPTIMAL_CLUSTERS: int = Field(default=4)


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
