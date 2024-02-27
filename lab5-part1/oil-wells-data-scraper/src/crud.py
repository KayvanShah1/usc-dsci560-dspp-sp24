import json
from typing import List
import itertools
import model
import schema
from settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def bulk_ingest_raw(requests: List[schema.RawWellData], db: Session):
    new_docs = []

    for np in requests:
        new_post = model.RawWellDataModel(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs


def get_all_ids(db: Session):
    """
    Retrieve IDs and content of the latest 10 documents from the RedditPostNew table.

    Args:
        db (Session): SQLAlchemy database session.
    """
    posts = db.query(model.RawWellDataModel.api_no).all()

    # Create a list of dictionaries containing IDs and content of each post
    posts_with_ids_and_content = [json.loads(doc[0]) for doc in posts]
    posts_with_ids_and_content = set(itertools.chain.from_iterable(posts_with_ids_and_content))
    return list(posts_with_ids_and_content)


def document_exists(id: str, db: Session):
    blog = db.query(model.CleanWellDataModel).filter(model.CleanWellDataModel.api_no == id).first()
    if blog:
        logger.error(
            f"Document with the id '{id}' already exists",
        )
        return True
    return False


def bulk_ingest_clean(requests: List[schema.CleanWellData], db: Session):
    new_docs = []

    for np in requests:
        new_post = model.CleanWellDataModel(**np.model_dump())
        new_docs.append(new_post)

    db.bulk_save_objects(new_docs)
    db.commit()

    logger.info(f"Successfully added '{len(new_docs)}' documents to the database")
    return new_docs
