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


def get_all_ids_and_content(db: Session):
    """
    Retrieve IDs and content of the latest 10 documents from the RedditPostNew table.

    Args:
        db (Session): SQLAlchemy database session.
    """
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


def fetch_posts_embeddings(db: Session):
    embeddings_list = db.query(model.EmbeddingVector.reddit_post_id, model.EmbeddingVector.embedding).all()

    # Create a list of dictionaries containing IDs and content of each post
    embeddings = [
        schema.EmbeddingsModel(reddit_post_id=post.reddit_post_id, embedding=post.embedding).get_embedding_array()
        for post in embeddings_list
    ]
    return embeddings


def get_titles_for_document_ids(db: Session, documents: list):
    # Query the database for titles corresponding to the given document IDs

    ids = [doc_id[0] for doc_id in documents]
    scores = [doc_id[1] for doc_id in documents]

    titles = (
        db.query(
            model.RedditPostNew.id,
            model.RedditPostNew.title,
            model.RedditPostNew.permalink,
            model.RedditPostNew.content,
        )
        .filter(model.RedditPostNew.id.in_(ids))
        .all()
    )

    # Create a list of dictionaries containing ID, title, permalink, and score
    title_list = []
    for id_, title, permalink, content in titles:
        score = scores[ids.index(id_)]  # Get the score corresponding to the current ID
        title_dict = {"id": id_, "title": title, "score": score, "permalink": permalink, "content": content}
        title_list.append(title_dict)

    return title_list
