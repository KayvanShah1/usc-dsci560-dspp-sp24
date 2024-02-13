from datetime import datetime
from time import time

import crud
import praw
import schema
from database import get_db
from extract import TextCleaner, TextPreprocessor, extract_keywords, get_text, initialize_driver
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


def create_submission_dict(submission, driver):
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

    content = get_text(submission_dict["url"], driver)
    submission_dict["content"] = TextCleaner.clean_text(content)
    submission_dict["keywords"] = ",".join(extract_keywords(TextCleaner.clean_text(submission_dict["content"])))
    submission_dict["content"] = TextPreprocessor.preprocess_text(submission_dict["content"])

    return submission_dict


def validate_post_data(submission_dict):
    """Validates the post data and return a data model instance"""
    return schema.RedditPostModel(**submission_dict)


def scrape_subreddit_posts(subreddit_name, new_post_count=100):
    """
    Scrape posts from a subreddit.
    """
    driver = initialize_driver()
    reddit = initialize_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    post_count = 0

    for submission in subreddit.new(limit=None):
        try:
            if not crud.post_exists(submission.id, db):
                # Process each submission here
                submission_dict = create_submission_dict(submission, driver)

                post_data = validate_post_data(submission_dict)
                crud.create(post_data, db)

                # Increment the post counter
                post_count += 1
                # Check if the desired number of posts has been scraped
                if post_count >= new_post_count:
                    break

        except praw.exceptions.APIException as e:
            # Handle rate limit exceeded error
            if e.error_type == "RATELIMIT":
                # Sleep for the recommended time specified by Reddit's API
                logger.error("Rate limit exceeded. Sleeping for '{}' seconds.".format(e.sleep_time))
                time.sleep(e.sleep_time)
                continue
            else:
                # Handle other API exceptions
                logger.exception("API Exception:", e)
                continue

    driver.close()


def main():
    subreddit_name = "tech"
    new_post_count = 100

    scrape_subreddit_posts(subreddit_name, new_post_count)


if __name__ == "__main__":
    main()
