import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Path:
    curr_file_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(curr_file_dir)
    env_file = os.path.join(root_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path.env_file, extra="ignore", env_file_encoding="utf-8"
    )

    MONGODB_URI: str = Field()


@lru_cache
def get_settings():
    return Settings()


config = get_settings()
