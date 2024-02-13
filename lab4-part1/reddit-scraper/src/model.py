from sqlalchemy import Column, Integer, String, Float, DateTime, Text

from database import Base, engine


class RedditPost(Base):
    __tablename__ = "tech"

    id = Column(String(30), primary_key=True)
    title = Column(Text)
    author = Column(String(50))
    num_comments = Column(Integer)
    url = Column(Text)
    selftext = Column(Text)
    created_utc = Column(DateTime)
    upvote_ratio = Column(Float)
    score = Column(Integer)
    num_crossposts = Column(Integer)
    preview = Column(Text, nullable=True)
    permalink = Column(Text)
    domain = Column(String(255))
    content = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)


Base.metadata.create_all(engine)
