from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import config, Path

SQLALCHAMY_DATABASE_URL = (
    f"mysql+pymysql://{config.MYSQL_USERNAME}:{config.MYSQL_PASSWORD}"
    f"@{config.MYSQL_HOST}:{config.MYSQL_PORT}/reddit_posts"
)

engine = create_engine(
    SQLALCHAMY_DATABASE_URL,
    connect_args={
        "connect_timeout": 30,
        "read_timeout": 10,
        "write_timeout": 10,
        "ssl": {"ca": Path.ca_cert_file},
    },
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
