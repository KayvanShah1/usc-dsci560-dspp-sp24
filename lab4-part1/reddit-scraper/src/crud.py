import model
import schema
from settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def get_all(db: Session):
    blogs = db.query(model.RedditPost).all()
    return blogs


def create(request: schema.RedditPostModel, db: Session):
    new_post = model.RedditPost(**request.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def post_exists(id: str, db: Session):
    blog = db.query(model.RedditPost).filter(model.RedditPost.id == id).first()
    if not blog:
        logger.warning(
            f"Blog with the id {id} is not available",
        )
        return False
    return True
