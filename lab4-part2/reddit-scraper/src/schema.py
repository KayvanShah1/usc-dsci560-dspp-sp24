import json
from datetime import datetime
from typing import Optional

import numpy as np
from pydantic import BaseModel


class RedditPostModel(BaseModel):
    id: str
    title: str
    author: str
    num_comments: int
    url: str
    selftext: str
    created_utc: datetime
    upvote_ratio: float
    score: int
    num_crossposts: int
    preview: Optional[str]
    permalink: str
    domain: str
    content: Optional[str]
    keywords: Optional[str]


class RedditPostModelNew(BaseModel):
    id: str
    title: str
    author: str
    num_comments: int
    url: str
    selftext: str
    created_utc: datetime
    upvote_ratio: float
    score: int
    num_crossposts: int
    preview: Optional[str]
    permalink: str
    domain: str
    # raw_content: Optional[str]
    content: Optional[str]
    keywords: Optional[str]


class RedditPostTextModel(BaseModel):
    id: str
    content: str


class EmbeddingData(BaseModel):
    reddit_post_id: str
    embedding_array: np.ndarray

    class Config:
        arbitrary_types_allowed = True


class EmbeddingsModel(BaseModel):
    reddit_post_id: str
    embedding: str

    def get_embedding_array(self):
        # Deserialize the JSON string into a Python dictionary
        embedding = json.loads(self.embedding)
        embedding_array = np.array(list(embedding), dtype=float)

        return EmbeddingData(reddit_post_id=self.reddit_post_id, embedding_array=embedding_array)
