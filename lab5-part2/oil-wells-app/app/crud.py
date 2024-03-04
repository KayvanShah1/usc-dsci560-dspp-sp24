import app.model as model
import app.schema as schema
from app.settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def get_all_clean(db: Session):
    """
    Retrieve all oil wells data from clean table

    Args:
        db (Session): SQLAlchemy database session.
    """
    posts = db.query(model.CleanWellDataModel).all()
    posts = schema.WellsData(data=[schema.CleanWellData(**post.__dict__) for post in posts])
    return posts
