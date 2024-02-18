import sys
import threading
import time
from datetime import datetime

import crud
import pandas as pd
import praw
import schema
from clustering import infer_clusters, load_kmeans_model
from database import get_db
from doc2vec import get_embedding_vector, load_emb_model
from extract import TextCleaner, TextPreprocessor, extract_keywords, get_text, initialize_driver
from settings import config, get_logger

logger = get_logger(__file__)

db = get_db()
emb_model = load_emb_model()
kmeans_model = load_kmeans_model()


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

    raw_content = get_text(submission_dict["url"], driver)
    submission_dict["content"] = TextCleaner.clean_text(submission_dict["title"] + " " + raw_content)
    submission_dict["keywords"] = ",".join(extract_keywords(submission_dict["content"]))
    submission_dict["content"] = TextPreprocessor.preprocess_text(submission_dict["content"])

    return submission_dict


def validate_post_data(submission_dict):
    """Validates the post data and return a data model instance"""
    return schema.RedditPostModelNew(**submission_dict)


def scrape_subreddit_posts(subreddit_name):
    """
    Scrape posts from a subreddit.
    """
    driver = initialize_driver()
    reddit = initialize_reddit_client()
    subreddit = reddit.subreddit(subreddit_name)

    post_data_list = []  # List to store post data

    for submission in subreddit.new(limit=50):
        try:
            if not crud.post_exists(submission.id, db):
                # Process each submission here
                submission_dict = create_submission_dict(submission, driver)

                post_data = validate_post_data(submission_dict)

                # Append post data to the list
                logger.info(
                    f"Post with id '{submission.id}' not found in the database. Post data has been extracted,"
                    " processed, and added to the update queue."
                )
                post_data_list.append(post_data)

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

    # Perform bulk insertion of post data
    if len(post_data_list) > 0:
        logger.info(f"Found '{len(post_data_list)}' new posts to be added")
        crud.bulk_create(post_data_list, db)
    else:
        logger.info("No new posts were found")


def background_task(subreddit_name, interval_minutes, stop_event):
    """
    Background task for updating the database at regular intervals.
    """
    while not stop_event.is_set():
        logger.info(f"Fetching data from subreddit '{subreddit_name}'...")
        scrape_subreddit_posts(subreddit_name)
        logger.info(f"Waiting for {interval_minutes} minutes before fetching data again...")
        stop_event.wait(interval_minutes * 60)  # Convert minutes to seconds


def infer_user_input(text: str):
    try:
        embedding_array = get_embedding_vector(text, emb_model)

        logger.info("Infering the user input")
        cluster = infer_clusters([embedding_array], kmeans_model)[0]
        logger.info(f"The predicted cluster for the random record is: {cluster}")
        similar_documents_ids = emb_model.docvecs.most_similar([embedding_array], topn=10)
        similar_documents = pd.DataFrame(crud.get_titles_for_document_ids(db, similar_documents_ids))
        columns = similar_documents.columns[:4]
        logger.info("Top 10 similar documents:")
        for i in similar_documents.loc[:, columns].to_dict(orient="records"):
            logger.info(i)

        content_text = ",".join(
            [TextPreprocessor.preprocess_text(TextCleaner.clean_text(i)) for i in similar_documents["title"]]
        )
        keywords = extract_keywords(content_text)
        logger.info("Keywords: %s", keywords)
    except Exception:
        logger.exception("No similar documents found")
        pass


def main():
    subreddit_name = "tech"

    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <interval_in_minutes>\nExample: python main.py 5")
        sys.exit(1)

    # Parse the interval argument
    try:
        interval_minutes = float(sys.argv[1])
    except ValueError:
        logger.error("Interval must be a 'number'")
        logger.info("Usage: python main.py <interval_in_minutes>\nExample: python main.py 5")
        sys.exit(1)

    # Create a stop event to signal when to stop the background task
    stop_event = threading.Event()

    # Start the background task in a separate thread
    background_thread = threading.Thread(target=background_task, args=(subreddit_name, interval_minutes, stop_event))
    background_thread.start()

    while background_thread.is_alive():
        user_input = input("Enter keywords or 'quit' to stop: ")
        if user_input.strip().lower() == "quit":
            logger.info("Stopping the background thread and exiting.")
            break
        logger.info(f"Analysing user input: '{user_input[:300]}...' ...")
        infer_user_input(user_input)

    # Set the stop event to stop the background task
    stop_event.set()

    # Wait for the background thread to finish
    background_thread.join()

    logger.info("Background task stopped.\nExited with code 0")


if __name__ == "__main__":
    main()
