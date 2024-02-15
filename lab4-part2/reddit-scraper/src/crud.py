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


def post_exists(id: str, db: Session):
    blog = db.query(model.RedditPostNew).filter(model.RedditPostNew.id == id).first()
    if blog:
        logger.error(
            f"Blog with the id '{id}' is already exists",
        )
        return True
    return False
