from typing import List
import model
import schema
from settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def get_all(db: Session):
    blogs = db.query(model.RedditPostNew).all()
    return blogs


def create(request: schema.RedditPostModelNew, db: Session):
    new_post = model.RedditPostNew(**request.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    logger.info(f"Successfully added post data with id '{request.id}' to the database")
    return new_post


def bulk_create(requests: List[schema.RedditPostModelNew], db: Session):
    new_posts = []

    for np in requests:
        new_post = model.RedditPostNew(**np.model_dump())
        new_posts.append(new_post)

    db.bulk_save_objects(new_posts)
    db.commit()
    # db.refresh(new_post)

    # Extract the IDs of the newly inserted posts
    for post in new_posts:
        logger.info(f"Successfully added post data with id '{post.id}' to the database")

    logger.info(f"Successfully added '{len(new_posts)}' posts to the database")
    return new_posts


def post_exists(id: str, db: Session):
    blog = db.query(model.RedditPostNew).filter(model.RedditPostNew.id == id).first()
    if blog:
        logger.error(
            f"Blog with the id '{id}' is already exists",
        )
        return True
    return False


def get_all_ids_and_content(db: Session) -> List[dict]:
    """
    Retrieve IDs and content of the latest 10 documents from the RedditPostNew table.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        List[dict]: A list of dictionaries containing IDs and content of each document.
    """
    # Retrieve the latest 10 documents ordered by ID in descending order
    posts = db.query(model.RedditPostNew.id, model.RedditPostNew.content).all()

    # Create a list of dictionaries containing IDs and content of each post
    posts_with_ids_and_content = [
        schema.RedditPostTextModel(id=post.id, content=post.content) for post in posts if post.content
    ]
    return posts_with_ids_and_content


def bulk_insert_embeddings(requests: List[schema.EmbeddingsModel], db: Session):
    new_posts = []

    for np in requests:
        new_post = model.EmbeddingVector(**np.model_dump())
        new_posts.append(new_post)

    db.bulk_save_objects(new_posts)
    db.commit()

    logger.info(f"Successfully added '{len(new_posts)}' embeddings to the database")
    return new_posts
