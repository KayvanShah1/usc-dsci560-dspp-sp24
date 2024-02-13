from datetime import datetime
from time import time

import crud
import praw
import schema
from database import get_db
from extract import TextCleaner, TextPreprocessor, extract_keywords, get_text
from settings import config, get_logger

logger = get_logger(__file__)

db = get_db()


def initialize_reddit_client():
    """
    Initialize the Reddit API client.
    """
    return praw.Reddit(
        client_id=config.REDDIT_PRAW_API_CLIENT_ID,
        client_secret=config.REDDIT_PRAW_API_CLIENT_SECRET_KEY,
        user_agent=config.USER_AGENT,
    )


def create_submission_dict(submission):
    """
    Create a dictionary representing a Reddit submission.
    """
    submission_dict = {
        "id": submission.id,
        "title": submission.title,
        "author": str(submission.author),
        "num_comments": submission.num_comments,
        "url": submission.url,
        "selftext": submission.selftext,
        "created_utc": datetime.utcfromtimestamp(submission.created_utc),
        "upvote_ratio": submission.upvote_ratio,
        "score": submission.score,
        "num_crossposts": submission.num_crossposts,
        "preview": None,
        "permalink": f"{config.REDDIT_BASE_URL}{submission.permalink}",
        "domain": submission.domain,
        "content": "",
        "keywords": "",
    }

    if hasattr(submission, "preview"):
        submission_dict["preview"] = submission.preview["images"][0]["source"]["url"]

    content = get_text(submission_dict["url"])
    submission_dict["content"] = TextCleaner.clean_text(content)
    submission_dict["keywords"] = ",".join(extract_keywords(TextCleaner.clean_text(submission_dict["content"])))
    submission_dict["content"] = TextPreprocessor.preprocess_text(submission_dict["content"])

    return submission_dict


reddit = praw.Reddit(
    client_id=config.REDDIT_PRAW_API_CLIENT_ID,
    client_secret=config.REDDIT_PRAW_API_CLIENT_SECRET_KEY,
    user_agent=config.USER_AGENT,
)

post_count = 0


subreddit = reddit.subreddit("tech")

for submission in subreddit.new(limit=None):
    try:
        if not crud.post_exists(submission.id, db):
            # Process each submission here
            submission_dict = {
                "id": submission.id,
                "title": submission.title,
                "author": str(submission.author),
                "num_comments": submission.num_comments,
                "url": submission.url,
                "selftext": submission.selftext,
                "created_utc": datetime.utcfromtimestamp(submission.created_utc),
                "upvote_ratio": submission.upvote_ratio,
                "score": submission.score,
                "num_crossposts": submission.num_crossposts,
                "preview": None,
                "permalink": f"{config.REDDIT_BASE_URL}{submission.permalink}",
                "domain": submission.domain,
                "content": "",
                "keywords": "",
            }

            if hasattr(submission, "preview"):
                submission_dict["preview"] = submission.preview["images"][0]["source"]["url"]

            content = get_text(submission_dict["url"])
            submission_dict["content"] = TextCleaner.clean_text(content)
            submission_dict["keywords"] = ",".join(extract_keywords(TextCleaner.clean_text(submission_dict["content"])))
            submission_dict["content"] = TextPreprocessor.preprocess_text(submission_dict["content"])

            # Increment the post counter
            post_count += 1
            post_data = schema.RedditPostModel(**submission_dict)
            crud.create(post_data, db)
            # logger.info(pretty_repr(x.__dict__))

            # Check if the desired number of posts has been scraped
            if post_count >= 10:
                break

    except praw.exceptions.APIException as e:
        # Handle rate limit exceeded error
        if e.error_type == "RATELIMIT":
            # Sleep for the recommended time specified by Reddit's API
            logger.error("Rate limit exceeded. Sleeping for {} seconds.".format(e.sleep_time))
            time.sleep(e.sleep_time)
            continue
        else:
            # Handle other API exceptions
            logger.exception("API Exception:", e)
            continue
