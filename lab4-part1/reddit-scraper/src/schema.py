from datetime import datetime
from typing import Optional

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
