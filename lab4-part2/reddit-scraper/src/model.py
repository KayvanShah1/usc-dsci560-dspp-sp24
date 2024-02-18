from database import Base, engine
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT, JSON
from sqlalchemy.orm import relationship


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


class RedditPostNew(Base):
    __tablename__ = "tech_new"

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
    content = Column(LONGTEXT, nullable=True)
    keywords = Column(Text, nullable=True)

    embedding_vector = relationship("EmbeddingVector", uselist=False, back_populates="reddit_post")


class EmbeddingVector(Base):
    __tablename__ = "embedding_vectors"

    reddit_post_id = Column(String(30), ForeignKey("tech_new.id"), primary_key=True)
    embedding = Column(JSON)

    reddit_post = relationship("RedditPostNew", back_populates="embedding_vector")


Base.metadata.create_all(engine)
