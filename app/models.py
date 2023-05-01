from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(Date, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User") #creates relation b/w Post class and User class

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

class Like(Base):
    __tablename__="likes"
    post_id = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)