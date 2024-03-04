import json
from typing import List
import itertools
import model
import schema
from settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def get_all_clean(db: Session):
    """
    Retrieve all oil wells data from clean table

    Args:
        db (Session): SQLAlchemy database session.
    """
    posts = db.query(model.CleanWellDataModel).all()
    return list(posts)
